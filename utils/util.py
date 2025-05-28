# File: util.py
############################################

# Imports
import asyncio
import aiohttp
from playsound import playsound


# Play sounds
async def play_sound(filename):
    await asyncio.to_thread(playsound, filename)


# Send fake local requests
async def send_fake_event(_type: str, event_data: dict):
    payload = {
        "subscription": {
            "type": _type
        },
        "event": event_data
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
                "http://localhost:8080/eventsub",  # or ngrok URL
                json=payload,
                headers={"X-Mock-Event": "true"}  # bypass signature
        ) as resp:
            return resp.status


def log(tag, message, color="\033[0m", space = False):
    prefix = "\n" if space else ""
    print(f"{prefix}{color}[{tag}]\033[0m {message}")
