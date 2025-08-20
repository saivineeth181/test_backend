import os
import requests
import time
import smtplib
from email.message import EmailMessage
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from detoxify import Detoxify
import pandas as pd


CHECK_INTERVAL = 120  # in seconds
TOXICITY_THRESHOLD = 0.75
SEXUAL_THRESHOLD = 0.65
REPEAT_LIMIT = 3

offender_log = {}

# Load lightweight toxic model (ToxiGen or ToxicBERT)
tokenizer = AutoTokenizer.from_pretrained("unitary/toxic-bert")
model = AutoModelForSequenceClassification.from_pretrained("unitary/toxic-bert")



def send_email_alert(username, comments):
    msg = EmailMessage()
    msg["Subject"] = f"Repeat Offender Alert: {username}"
    msg["From"] = BOT_EMAIL
    msg["To"] = ADMIN_EMAIL
    msg.set_content(f"User {username} posted {len(comments)} abusive comments:\n\n" + "\n\n".join(comments))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(BOT_EMAIL, EMAIL_PASSWORD)
        smtp.send_message(msg)


def is_toxic(comment):
    # inputs = tokenizer(comment, return_tensors="pt", truncation=True, padding=True)
    # with torch.no_grad():
    #     outputs = model(**inputs)
    # probs = torch.nn.functional.softmax(outputs.logits, dim=1)
    # toxic_score = probs[0][1].item()
    results = Detoxify('multilingual').predict(comment)
    print(f"Results: {results}")
    print(f"Comment: {comment} | Toxicity Score: {results['toxicity']}")
    return results["toxicity"] >= TOXICITY_THRESHOLD


def fetch_recent_media():
    url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media?fields=id,caption,timestamp&access_token={ACCESS_TOKEN}"
    res = requests.get(url)
    return res.json().get("data", [])


def fetch_comments(media_id):
    url = f"https://graph.facebook.com/v18.0/{media_id}/comments?access_token={ACCESS_TOKEN}"
    res = requests.get(url)
    return res.json().get("data", [])


def delete_comment(comment_id):
    url = f"https://graph.facebook.com/v18.0/{comment_id}?access_token={ACCESS_TOKEN}"
    res = requests.delete(url)
    return res.status_code == 200


def process_comment(comment, media_id):
    text = comment.get("text", "")
    user = comment.get("username", "unknown")
    comment_id = comment["id"]

    if is_toxic(text):
        print(f"[DELETED] Toxic comment by {user}: {text}")
        delete_comment(comment_id)

        # Log offender
        if user not in offender_log:
            offender_log[user] = {"count": 0, "comments": []}
        offender_log[user]["count"] += 1
        offender_log[user]["comments"].append(text)

        # Trigger alert
        # if offender_log[user]["count"] >= REPEAT_LIMIT:
        #     send_email_alert(user, offender_log[user]["comments"])
        #     offender_log[user]["count"] = 0  # reset after alert


def monitor_loop():
    print("🛡️ Starting Instagram Moderation Bot...")
    while True:
        try:
            media_items = fetch_recent_media()
            for media in media_items:
                comments = fetch_comments(media["id"])
                for comment in comments:
                    process_comment(comment, media["id"])

            print("✅ Scan complete. Sleeping...")
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    print(is_toxic("slut"))
