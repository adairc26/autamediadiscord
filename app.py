from flask import Flask, request, jsonify, make_response
import requests
from datetime import datetime
import os

app = Flask(__name__)

DISCORD_WEBHOOK_URL = os.environ.get(
    'DISCORD_WEBHOOK_URL',
    'https://discord.com/api/webhooks/1464849408100274358/zoJIBWaFhTdEPUx2SnjoAEyf-no6kXlAYjmI44jwsNQcfZLIDzzQ2_qEpNHLpom2DOf9'
)

@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/')
def home():
    return jsonify({"status": "Ripple Strategies — Notification Service Active"})

@app.route('/contact', methods=['POST', 'OPTIONS'])
def contact():
    if request.method == 'OPTIONS':
        return make_response('', 204)

    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "message": "No data received"}), 400

        name    = data.get('name', 'Unknown')
        email   = data.get('email', 'Not provided')
        message = data.get('message', 'No message')

        embed = {
            "title": "📬 New Contact Form Submission",
            "color": 1752220,
            "fields": [
                {"name": "👤 Name",    "value": name,    "inline": True},
                {"name": "📧 Email",   "value": email,   "inline": True},
                {"name": "💬 Message", "value": message, "inline": False},
            ],
            "footer": {"text": "Ripple Strategies — Website Contact Form"},
            "timestamp": datetime.utcnow().isoformat()
        }

        discord_payload = {
            "content": "🔔 **New message from the Ripple Strategies website!**",
            "embeds": [embed]
        }

        response = requests.post(DISCORD_WEBHOOK_URL, json=discord_payload, timeout=5)

        if response.status_code == 204:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": "Discord error"}), 500

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
