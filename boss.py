import os
import sys
import json
import time
import requests
import websocket
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def main():
    return '<meta http-equiv="refresh" content="0; URL=https://example.com"/>'

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    server = Thread(target=run)
    server.start()

status = os.getenv("status")  # online/dnd/idle
custom_status = os.getenv("custom_status")  # Custom status message
emoji_name = os.getenv("emoji_name")  # Emoji name for the custom status
emoji_id = os.getenv("emoji_id")  # Emoji ID for the custom status
emoji_animated = os.getenv("emoji_animated", "false").lower() == "true"  # Whether the emoji is animated
client_id = os.getenv("client_id")  # Discord application client ID
large_image = os.getenv("large_image")  # Large image key for Rich Presence
large_text = os.getenv("large_text")  # Large image hover text for Rich Presence
small_image = os.getenv("small_image")  # Small image key for Rich Presence
small_text = os.getenv("small_text")  # Small image hover text for Rich Presence
details = os.getenv("details")  # Details for Rich Presence
state = os.getenv("state")  # State for Rich Presence
mode = os.getenv("mode")  # Mode for Rich Presence (playing/listening/watching)
usertoken = os.getenv("token")

if not usertoken:
    print("[ERROR] Please add a token inside Secrets.")
    sys.exit()

headers = {"Authorization": usertoken, "Content-Type": "application/json"}

validate = requests.get("https://canary.discordapp.com/api/v9/users/@me", headers=headers)
if validate.status_code != 200:
    print("[ERROR] Your token might be invalid. Please check it again.")
    sys.exit()

userinfo = requests.get("https://canary.discordapp.com/api/v9/users/@me", headers=headers).json()
username = userinfo["username"]
discriminator = userinfo["discriminator"]
userid = userinfo["id"]

def onliner(token, status):
    ws = websocket.WebSocket()
    ws.connect("wss://gateway.discord.gg/?v=9&encoding=json")
    start = json.loads(ws.recv())
    heartbeat = start["d"]["heartbeat_interval"]
    auth = {
        "op": 2,
        "d": {
            "token": token,
            "properties": {
                "$os": "Windows",
                "$browser": "Discord Client",
                "$device": "desktop",
            },
            "presence": {"status": status, "afk": False},
        },
        "s": None,
        "t": None,
    }
    ws.send(json.dumps(auth))
    
    activities = {
        "type": 4,
        "state": custom_status,
        "name": "Custom Status",
        "id": "custom",
    }
    if emoji_name:
        activities["emoji"] = {"name": emoji_name, "animated": emoji_animated}
        if emoji_id:
            activities["emoji"]["id"] = emoji_id
    
    cstatus = {
        "op": 3,
        "d": {
            "since": 0,
            "activities": [activities],
            "status": status,
            "afk": False,
        },
    }

    if client_id:
        if mode == "playing":
            cstatus["d"]["activities"].append({
                "name": "Sample Game",
                "type": 0,
                "state": state,
                "details": details,
                "timestamps": {
                    "start": int(time.time())
                },
                "assets": {
                    "large_image": large_image,
                    "large_text": large_text,
                    "small_image": small_image,
                    "small_text": small_text
                }
            })
        elif mode == "listening":
            cstatus["d"]["activities"].append({
                "name": state,
                "type": 2,
                "details": details,
                "state": "Listening",
                "timestamps": {
                    "start": int(time.time())
                },
                "assets": {
                    "large_image": large_image,
                    "large_text": large_text,
                    "small_image": small_image,
                    "small_text": small_text
                }
            })
        elif mode == "watching":
            cstatus["d"]["activities"].append({
                "name": state,
                "type": 3,
                "state": details,
                "timestamps": {
                    "start": int(time.time())
                },
                "assets": {
                    "large_image": large_image,
                    "large_text": large_text,
                    "small_image": small_image,
                    "small_text": small_text
                }
            })

    ws.send(json.dumps(cstatus))
    online = {"op": 1, "d": "None"}
    time.sleep(heartbeat / 1000)
    ws.send(json.dumps(online))

def run_onliner():
    os.system("clear")
    print(f"Logged in as {username}#{discriminator} ({userid}).")
    while True:
        onliner(usertoken, status)
        time.sleep(30)

keep_alive()
run_onliner()
