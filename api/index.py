from flask import Flask, request
import requests
import os
import json

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAATLbkq5LgwBSpHYpd3rSvFUdbUpa7lWIJlZALcCHpi8NCrpaa6qS39dpREZCAdY5BSnRuIHIRGXVZARNd6b35vMsNQYCoirKZABvXz7zQhSb72mynaSxroIiAvV6cPnM8AAlmeFTmOiaDpZBWZA2pC7eT3m9zsOCJQKkkirZAjZCLbWILcdt97ioIPcuUJ2nOfaYtigjQZDZD"
VERIFY_TOKEN = "ABCD1234"


@app.route("/", methods=["GET"])
def home():
    return "Facebook Bot Online", 200


# Facebook Webhook verification
@app.route("/webhook", methods=["GET"])
def verify():

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Forbidden", 403


# Facebook messages
@app.route("/webhook", methods=["POST"])
def webhook():

    payload = request.get_json(silent=True)

    print("========== PAYLOAD ==========")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("=============================")

    if not payload:
        return "OK", 200

    if payload.get("object") != "page":
        return "OK", 200

    # كل entry
    for entry in payload.get("entry", []):

        # كل message
        for event in entry.get("messaging", []):

            sender_id = event.get("sender", {}).get("id")

            if not sender_id:
                continue

            # نرجعو نفس event كامل للمستخدم
            reply = json.dumps(
                event,
                indent=2,
                ensure_ascii=False
            )

            send_message(sender_id, reply)

    return "EVENT_RECEIVED", 200


def send_message(sender_id, text):

    url = "https://graph.facebook.com/v23.0/me/messages"

    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }

    data = {
        "recipient": {
            "id": sender_id
        },
        "message": {
            "text": text
        }
    }

    r = requests.post(
        url,
        params=params,
        json=data,
        timeout=20
    )

    print("Facebook:", r.status_code, r.text)


if __name__ == "__main__":
    app.run()
