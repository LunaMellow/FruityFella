import requests
from classes.consts import Consts

headers = {
    "Client-ID": Consts.CLIENT_ID,
    "Authorization": f"Bearer {Consts.ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def subscribe(event_type, condition):
    data = {
        "type": event_type,
        "version": "1",
        "condition": condition,
        "transport": {
            "method": "webhook",
            "callback": Consts.CALLBACK_URL,
            "secret": Consts.SECRET
        }
    }
    r = requests.post("https://api.twitch.tv/helix/eventsub/subscriptions", headers=headers, json=data)
    print(f"{event_type}: {r.status_code} - {r.text}")

def register_all():
    uid = Consts.BROADCASTER_ID
    subscribe("channel.channel_points_custom_reward_redemption.add", {"broadcaster_user_id": uid})
    subscribe("channel.subscribe", {"broadcaster_user_id": uid})
    subscribe("channel.cheer", {"broadcaster_user_id": uid})

if __name__ == "__main__":
    register_all()
