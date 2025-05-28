# File: run_all.py
############################################

import subprocess
import time
import requests
import json
import os
import utils.util as util

# Config
NGROK_API_URL = "http://localhost:4040/api/tunnels"
TWITCH_EVENTSUB_URL = "https://api.twitch.tv/helix/eventsub/subscriptions"
CALLBACK_PATH = "/eventsub"

# Environment (from env vars)
OAUTH_TOKEN = os.getenv("TWITCH_ACCESS_TOKEN")
CLIENT_ID = os.getenv("TWITCH_PLUMHOE_CLIENT_ID")
CHANNEL_ID = os.getenv("TWITCH_BROADCASTER_ID")
EVENTSUB_SECRET = os.getenv("TWITCH_SECRET")

def clean_old_eventsubs():
    print("[Cleanup] Checking for existing EventSub subscriptions to remove...")

    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {OAUTH_TOKEN}"
    }

    response = requests.get(TWITCH_EVENTSUB_URL, headers=headers)
    if response.status_code != 200:
        print(f"[Error] Could not fetch subscriptions: {response.status_code}")
        return

    subs = response.json().get("data", [])
    for sub in subs:
        if sub["type"] == "channel.channel_points_custom_reward_redemption.add":
            condition = sub.get("condition", {})
            if condition.get("broadcaster_user_id") == CHANNEL_ID:
                sub_id = sub["id"]
                del_resp = requests.delete(f"{TWITCH_EVENTSUB_URL}?id={sub_id}", headers=headers)
                print(f"[Cleanup] Deleted sub {sub_id} → {del_resp.status_code}")


# Start ngrok
print("[Boot] Starting ngrok tunnel...")
ngrok_proc = subprocess.Popen(["ngrok", "http", "8080"])
time.sleep(2)

# Get public URL from ngrok
print("[Boot] Fetching public URL from ngrok...")
try:
    tunnels = requests.get(NGROK_API_URL).json()
    public_url = next(tunnel['public_url'] for tunnel in tunnels['tunnels'] if tunnel['proto'] == 'https')
    callback_url = public_url + CALLBACK_PATH
except Exception as e:
    print(f"[Error] Could not get ngrok URL: {e}")
    ngrok_proc.kill()
    exit(1)

print(f"[ngrok] Public URL: {callback_url}")

# Register EventSub subscription
print("[Boot] Registering EventSub webhook for channel point redemptions...")
headers = {
    "Client-ID": CLIENT_ID,
    "Authorization": f"Bearer {OAUTH_TOKEN}",
    "Content-Type": "application/json"
}
payload = {
    "type": "channel.channel_points_custom_reward_redemption.add",
    "version": "1",
    "condition": {
        "broadcaster_user_id": CHANNEL_ID
    },
    "transport": {
        "method": "webhook",
        "callback": callback_url,
        "secret": EVENTSUB_SECRET
    }
}
clean_old_eventsubs()
resp = requests.post(TWITCH_EVENTSUB_URL, headers=headers, json=payload)
if resp.status_code == 202:
    print("[Twitch] EventSub webhook registered successfully!")
else:
    print(f"[Twitch] Failed to register EventSub: {resp.status_code}\n{resp.text}")
    ngrok_proc.kill()
    exit(1)

# Start EventSub Server
print("\n[Boot] Starting eventsub_server.py...\n")
eventsub_proc = subprocess.Popen(["python", "utils/eventsub_server.py"])
time.sleep(1)

# Start FruityFella Bot
print("\n[Boot] Starting FruityFella bot...\n")
bot_proc = subprocess.Popen(["python", "main.py"])

# Wait for all processes
try:
    while True:
        time.sleep(5)
except KeyboardInterrupt:
    print("\n[Shutdown] Cleaning up...")
    ngrok_proc.terminate()
    eventsub_proc.terminate()
    bot_proc.terminate()
    print("[Shutdown] All processes terminated.")
