# File: hue_client.py
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
                print(f"Forwarded to bot with status {resp.status}")
        except Exception as e:
            print(f"Failed to forward reward: {e}")

async def forward_cheer(user, bits):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "http://localhost:6969/trigger",
                json={"user": user, "bits": bits}
            ) as resp:
                print(f"Forwarded cheer to bot: {resp.status}")
        except Exception as e:
            print(f"Cheer forward failed: {e}")

async def handle_eventsub(request):
    body = await request.read()

    is_local_request = request.remote in ("127.0.0.1", "::1", "localhost")
    if not is_local_request and not verify_signature(request, body):
        print("Signature verification failed.")
        return web.Response(status=403)

    data = json.loads(body.decode())

    #print("Received raw body:")
    #print(json.dumps(data, indent=2))

    if data.get("challenge"):
        print("Responding to challenge verification.")
        return web.Response(text=data["challenge"])

    event_type = data["subscription"]["type"]
    event = data["event"]

    print(f"Received event: {event_type}")

    if event_type == "channel.channel_points_custom_reward_redemption.add":
        reward = event["reward"]["title"]
        print(f"Channel Point Redeemed: {reward}")

        asyncio.create_task(forward_reward(reward))

    elif event_type == "channel.subscribe":
        print(f"{event['user_name']} just subscribed!")


    elif event_type == "channel.cheer":
        user = event["user_name"]
        bits = int(event["bits"])
        print(f"{user} cheered {bits} bits!")
        asyncio.create_task(forward_cheer(user, bits))

    return web.Response(status=200)

app.router.add_post("/eventsub", handle_eventsub)

if __name__ == "__main__":
    web.run_app(app, port=8080)