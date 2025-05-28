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
from utils.util import log

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
                log("Event", f"Forwarded to bot with status {resp.status}\n", "\033[92m")
        except Exception as e:
            log("Event", f"Failed to forward reward: {e}", "\033[91m")

async def forward_cheer(user, bits):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "http://localhost:6969/trigger",
                json={"user": user, "bits": bits}
            ) as resp:
                log("Event", f"Forwarded cheer to bot: {resp.status}", "\033[92m")
        except Exception as e:
            log("Event", f"Cheer forward failed: {e}", "\033[91m")

async def handle_eventsub(request):
    body = await request.read()

    log("EventSub", "=== EventSub request received ===", "\033[94m", True)
    log("Headers", str(request.headers), "\033[90m")

    raw = body.decode()
    parsed = json.loads(raw)

    log("Body", json.dumps(parsed, indent=2), "\033[90m")

    is_local_request = request.remote in ("127.0.0.1", "::1", "localhost")
    if not is_local_request and not verify_signature(request, body):
        log("Data", "Signature verification failed.", "\033[91m")
        return web.Response(status=403)

    data = json.loads(body.decode())

    if data.get("challenge"):
        log("Data", "Responding to challenge verification.", "\033[94m")
        return web.Response(text=data["challenge"])

    if "subscription" not in data or "event" not in data:
        log("Data", "Invalid EventSub payload received", "\033[91m")
        return web.Response(status=400)

    log("Data", "Received raw body:", "\033[90m")
    log("JSON", json.dumps(data, indent=2), "\033[90m")

    event_type = data["subscription"]["type"]
    event = data["event"]

    log("Event", f"Received event: {event_type}", "\033[96m")

    if event_type == "channel.channel_points_custom_reward_redemption.add":
        reward = event["reward"]["title"]
        log("Points", f"Channel Point Redeemed: {reward}", "\033[92m")
        asyncio.create_task(forward_reward(reward))

    elif event_type == "channel.subscribe":
        user = event["user_name"]
        tier = event["tier"]
        is_prime = event.get("is_prime", False)
        log("Sub", f"{user} just subscribed!", "\033[95m")
        if is_prime:
            log("Type", "Prime sub!", "\033[94m")
        else:
            log("Type", f"Tier {int(tier) // 1000} sub!", "\033[94m")
        asyncio.create_task(forward_reward(f"sub{tier}"))

    elif event_type == "channel.follow":
        user = event["user_name"]
        log("Follow", f"New follower: {user}", "\033[93m")
        asyncio.create_task(forward_reward("follow"))

    elif event_type == "channel.cheer":
        user = event.get("user_name", "unknown")
        bits = int(event.get("bits", 0))
        log("Cheer", f"{user} just cheered {bits} bits!", "\033[96m")
        asyncio.create_task(forward_cheer(user, bits))

    return web.Response(status=200)

app.router.add_post("/eventsub", handle_eventsub)

if __name__ == "__main__":
    web.run_app(app, port=8080)