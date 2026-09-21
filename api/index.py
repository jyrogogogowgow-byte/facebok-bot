from flask import Flask, request
import requests
import os
import json

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAATLbkq5LgwBSpHYpd3rSvFUdbUpa7lWIJlZALcCHpi8NCrpaa6qS39dpREZCAdY5BSnRuIHIRGXVZARNd6b35vMsNQYCoirKZABvXz7zQhSb72mynaSxroIiAvV6cPnM8AAlmeFTmOiaDpZBWZA2pC7eT3m9zsOCJQKkkirZAjZCLbWILcdt97ioIPcuUJ2nOfaYtigjQZDZD"
VERIFY_TOKEN = "ABCD1234"


# تخزين مؤقت داخل نفس الـinstance
# سنستعمل comment_id لمنع التكرار أثناء حياة الـinstance
processed_comments = set()


REPLY_TEXT = "❤️ لا تنسى متابعة الصفحة لتتوصل بكل جديد!"


@app.route("/", methods=["GET"])
def home():
    return "Facebook Comment Bot Online ❤️", 200


# =========================
# WEBHOOK VERIFICATION
# =========================

@app.route("/webhook", methods=["GET"])
def verify():

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Forbidden", 403


# =========================
# FACEBOOK WEBHOOK
# =========================

@app.route("/webhook", methods=["POST"])
def webhook():

    payload = request.get_json(silent=True)

    print("\n========== FACEBOOK PAYLOAD ==========")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("======================================\n")

    if not payload:
        return "OK", 200

    # نتأكد أنه Page webhook
    if payload.get("object") != "page":
        return "OK", 200

    for entry in payload.get("entry", []):

        changes = entry.get("changes", [])

        for change in changes:

            # خاصنا comments
            if change.get("field") != "feed":
                continue

            value = change.get("value", {})

            # نتأكد أن الحدث ديال comment
            if value.get("item") != "comment":
                continue

            # بعض الأحداث تكون creation
            verb = value.get("verb")

            if verb and verb != "add":
                continue

            comment_id = value.get("comment_id")

            if not comment_id:
                print("No comment_id")
                continue

            # =========================
            # منع تكرار الرد
            # =========================

            if comment_id in processed_comments:

                print("Already processed:", comment_id)

                continue

            # نسجلو التعليق
            processed_comments.add(comment_id)

            # =========================
            # الرد على التعليق
            # =========================

            reply_to_comment(comment_id)


    return "EVENT_RECEIVED", 200


# =========================
# REPLY TO COMMENT
# =========================

def reply_to_comment(comment_id):

    url = f"https://graph.facebook.com/{comment_id}/comments"

    data = {
        "message": REPLY_TEXT,
        "access_token": PAGE_ACCESS_TOKEN
    }

    try:

        response = requests.post(
            url,
            data=data,
            timeout=15
        )

        print("COMMENT ID:", comment_id)
        print("REPLY STATUS:", response.status_code)
        print("REPLY RESPONSE:", response.text)

    except Exception as e:

        print("Reply error:", str(e))


# =========================
# VERCEL
# =========================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080))
    )
