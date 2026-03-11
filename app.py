from flask import Flask, request, jsonify, make_response
import requests
from datetime import datetime
import os
import time

app = Flask(__name__)

WEBHOOK_INQUIRY = "https://discord.com/api/webhooks/1480370483366072382/rq9qhNH36Uep-rtPs_ZrDCDv_7xY_bUmDN1a-fG6hB8PPZOtbXHt3nsvKhD5NtO3ka6q"
WEBHOOK_NOTIFY = "https://discord.com/api/webhooks/1480370399446569020/YkdY6T7nW1doJnvIbnH8njUBSeduTvAE1wyTp-dcAVgyzNXHt_5ce8qjinNX6Xs0Sh_l"


def post_discord(url, payload, retries=3):
    """Post to Discord with retry on 429 rate limit"""
    for i in range(retries):
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code != 429:
            return resp
        retry_after = resp.json().get("retry_after", 1000) / 1000  # ms → s
        print(f"[DISCORD] Rate limited, retrying in {retry_after}s...")
        time.sleep(retry_after)
    return resp  # return last response if all retries fail


@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/")
def home():
    return jsonify({"status": "Autamedia — Notification Service Active"})


@app.route("/contact", methods=["POST", "OPTIONS"])
def contact():
    if request.method == "OPTIONS":
        return make_response("", 204)
    try:
        data = request.json or {}
        name = data.get("name", "Unknown")
        email = data.get("email", "Not provided")
        message = data.get("message", "No message")

        embed = {
            "title": "New Project Inquiry",
            "color": 0xB8976A,
            "fields": [
                {"name": "Name", "value": name, "inline": True},
                {"name": "Email", "value": email, "inline": True},
                {"name": "Message", "value": message, "inline": False},
            ],
            "footer": {"text": "Autamedia — Contact Form"},
            "timestamp": datetime.utcnow().isoformat(),
        }

        resp = post_discord(WEBHOOK_INQUIRY, {
            "content": "**New inquiry from Autamedia website**",
            "embeds": [embed],
        })

        print(f"[CONTACT] Discord status: {resp.status_code} | {resp.text}")
        success = resp.status_code in (200, 204)
        return jsonify({"success": success, "message": "" if success else f"Discord {resp.status_code}"})

    except Exception as e:
        print(f"[CONTACT] Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/notify", methods=["POST", "OPTIONS"])
def notify():
    if request.method == "OPTIONS":
        return make_response("", 204)
    try:
        data = request.json or {}
        email = data.get("email", "Not provided")
        source = data.get("source", "Unknown")

        embed = {
            "title": "New Email Signup",
            "color": 0x7EAFC4,
            "fields": [
                {"name": "Email", "value": email, "inline": True},
                {"name": "Source", "value": source, "inline": True},
            ],
            "footer": {"text": "Autamedia — Notify Signup"},
            "timestamp": datetime.utcnow().isoformat(),
        }

        resp = post_discord(WEBHOOK_NOTIFY, {
            "content": "**Someone wants to stay updated!**",
            "embeds": [embed],
        })

        print(f"[NOTIFY] Discord status: {resp.status_code} | {resp.text}")
        success = resp.status_code in (200, 204)
        return jsonify({"success": success, "message": "" if success else f"Discord {resp.status_code}"})

    except Exception as e:
        print(f"[NOTIFY] Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True)
