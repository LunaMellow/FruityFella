# File: eventsub_server.py
############################################

# Imports
import asyncio
import hmac
import hashlib
import json
import aiohttp
from aiohttp import web
from classes.consts import Consts

def verify_signature(request, body: bytes):
    message_id = request.headers.get("Twitch-Eventsub-Message-Id", "")
    timestamp = request.headers.get("Twitch-Eventsub-Message-Timestamp", "")
    signature = request.headers.get("Twitch-Eventsub-Message-Signature", "")

    msg = message_id + timestamp + body.decode("utf-8")
    expected = "sha256=" + hmac.new(
        Consts.SECRET.encode(), msg.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

app = web.Application()

async def forward_reward(reward):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "http://localhost:6969/trigger",
                json={"reward": reward}
            ) as resp:
                print(f"[Event] Forwarded to bot with status {resp.status}")
        except Exception as e:
            print(f"[Event] Failed to forward reward: {e}")

async def forward_cheer(user, bits):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "http://localhost:6969/trigger",
                json={"user": user, "bits": bits}
            ) as resp:
                print(f"[Event] Forwarded cheer to bot: {resp.status}")
        except Exception as e:
            print(f"[Event] Cheer forward failed: {e}")

async def handle_eventsub(request):
    body = await request.read()

    print("=== EventSub request received ===")
    print(request.headers)
    print(body.decode())

    is_local_request = request.remote in ("127.0.0.1", "::1", "localhost")
    if not is_local_request and not verify_signature(request, body):
        print("[Data] Signature verification failed.")
        return web.Response(status=403)

    data = json.loads(body.decode())

    if data.get("challenge"):
        print("[Data] Responding to challenge verification.")
        return web.Response(text=data["challenge"])

    if "subscription" not in data or "event" not in data:
        print("[Data] Invalid EventSub payload received")
        return web.Response(status=400)

    print("\n[Data] Received raw body:")
    print(json.dumps(data, indent=2))

    event_type = data["subscription"]["type"]
    event = data["event"]

    print(f"\n[Event] Received event: {event_type}")

    if event_type == "channel.channel_points_custom_reward_redemption.add":
        print(f"Channel Points")
        reward = event["reward"]["title"]
        print(f"Channel Point Redeemed: {reward}")
        asyncio.create_task(forward_reward(reward))


    elif event_type == "channel.subscribe":
        user = event["user_name"]
        tier = event["tier"]
        is_prime = event.get("is_prime", False)
        print(f"\n{user} just subscribed!")
        if is_prime:
            print(f"[Type] Prime sub!")
        else:
            print(f"[Type] Tier {int(tier) // 1000} sub!")
        asyncio.create_task(forward_reward(f"sub{tier}"))


    elif event_type == "channel.follow":
        user = event["user_name"]
        print(f"\n[Event] New follower: {user}")
        asyncio.create_task(forward_reward("follow"))

    elif event_type == "channel.cheer":
        user = event.get("user_name", "unknown")
        bits = int(event.get("bits", 0))
        print(f"\n[Event] {user} just cheered {bits} bits!")
        asyncio.create_task(forward_cheer(user, bits))

    return web.Response(status=200)

app.router.add_post("/eventsub", handle_eventsub)

if __name__ == "__main__":
    web.run_app(app, port=8080)