from flask import Flask, request
import requests
import os
import json

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "ABCD1234")


# =========================
# إرسال رسالة للمستخدم
# =========================
def send_message(recipient_id, text):

    url = "https://graph.facebook.com/v23.0/me/messages"

    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }

    payload = {
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": text
        }
    }

    response = requests.post(
        url,
        params=params,
        json=payload,
        timeout=20
    )

    print("SEND STATUS:", response.status_code)
    print("SEND RESPONSE:", response.text)

    return response


# =========================
# Webhook Verification
# =========================
@app.route("/webhook", methods=["GET"])
def verify():

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


# =========================
# Facebook Webhook
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():

    # ناخدو الـpayload الخام كامل
    data = request.get_json(silent=True)

    print("\n================ WEBHOOK ================")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("=========================================\n")

    if not data:
        return "OK", 200

    # Facebook Messenger
    if data.get("object") == "page":

        for entry in data.get("entry", []):

            for messaging_event in entry.get("messaging", []):

                sender = messaging_event.get("sender", {})
                sender_id = sender.get("id")

                if not sender_id:
                    continue

                # نحول الـpayload كامل إلى JSON readable
                payload_text = json.dumps(
                    messaging_event,
                    indent=2,
                    ensure_ascii=False
                )

                # الرد للمستخدم
                send_message(
                    sender_id,
                    payload_text
                )

    return "EVENT_RECEIVED", 200


# =========================
# Home
# =========================
@app.route("/", methods=["GET"])
def home():
    return "Facebook Bot is running!", 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080))
    )
