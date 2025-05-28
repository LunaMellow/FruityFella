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
    util.log("Cleanup", "Checking for existing EventSub subscriptions to remove...", "\033[93m")

    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {OAUTH_TOKEN}"
    }

    response = requests.get(TWITCH_EVENTSUB_URL, headers=headers)
    if response.status_code != 200:
        util.log("Error", f"Could not fetch subscriptions: {response.status_code}", "\033[91m")
        return

    subs = response.json().get("data", [])
    for sub in subs:
        if sub["type"] == "channel.channel_points_custom_reward_redemption.add":
            condition = sub.get("condition", {})
            if condition.get("broadcaster_user_id") == CHANNEL_ID:
                sub_id = sub["id"]
                del_resp = requests.delete(f"{TWITCH_EVENTSUB_URL}?id={sub_id}", headers=headers)
                util.log("Cleanup", f"Deleted sub {sub_id} → {del_resp.status_code}", "\033[93m")

# Start ngrok
util.log("Boot", "Starting ngrok tunnel...", "\033[94m")
ngrok_proc = subprocess.Popen(["ngrok", "http", "8080"])
time.sleep(2)

# Get public URL from ngrok
util.log("Boot", "Fetching public URL from ngrok...", "\033[94m")
try:
    tunnels = requests.get(NGROK_API_URL).json()
    public_url = next(tunnel['public_url'] for tunnel in tunnels['tunnels'] if tunnel['proto'] == 'https')
    callback_url = public_url + CALLBACK_PATH
except Exception as e:
    util.log("Error", f"Could not get ngrok URL: {e}", "\033[91m")
    ngrok_proc.kill()
    exit(1)

util.log("ngrok", f"Public URL: {callback_url}", "\033[95m")

# Register EventSub subscription
util.log("Boot", "Registering EventSub webhook for channel point redemptions...", "\033[94m")
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
    util.log("Twitch", "EventSub webhook registered successfully!", "\033[92m")
else:
    util.log("Twitch", f"Failed to register EventSub: {resp.status_code}\n{resp.text}", "\033[91m")
    ngrok_proc.kill()
    exit(1)

# Start EventSub Server
util.log("Boot", "Starting eventsub_server.py...\n", "\033[94m", True)
eventsub_proc = subprocess.Popen(["python", "utils/eventsub_server.py"])
time.sleep(1)

# Start FruityFella Bot
util.log("Boot", "Starting FruityFella bot...", "\033[94m", True)
bot_proc = subprocess.Popen(["python", "main.py"])

# Wait for all processes
try:
    while True:
        time.sleep(5)
except KeyboardInterrupt:
    util.log("Shutdown", "Cleaning up...", "\033[91m", True)
    ngrok_proc.terminate()
    eventsub_proc.terminate()
    bot_proc.terminate()
    util.log("Shutdown", "All processes terminated.", "\033[91m")
