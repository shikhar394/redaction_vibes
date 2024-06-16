import os
import sys
import logging
import requests

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request, jsonify
from dotenv import dotenv_values

#----------------INIT TOKENS------------------------#
config = dotenv_values(".env")  # config = {"SLACK_BOT_TOKEN": "foo", "SLACK_SIGNING_SECRET": "fi"}
if not config["SLACK_BOT_TOKEN"] or not config["SLACK_SIGNING_SECRET"]:
    raise ValueError("Missing SLACK_BOT_TOKEN or SLACK_SIGNING_SECRET")

#--------------INIT MODULES-----------#
# Install the Slack app and get xoxb- token in advance
app = App(token=config["SLACK_BOT_TOKEN"], signing_secret=config["SLACK_SIGNING_SECRET"])
REDACTOR_URL = "http://localhost:3001/"

# Flask web server for the Slack events
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)
logging.basicConfig(level=logging.DEBUG)

#-----------INIT FUNCTIONS---------------#
# Listens to incoming messages
@app.event("message")
def handle_message_events(event, say):
    logging.debug(f"Event received: {event}")
    user = event.get('user')
    client_msg_id = event.get('client_msg_id')
    text = event.get('text')
    channel = event.get('channel')
    #print(f"Message from {user} in channel {channel}: {text}")
    text_redacted, stiched_text = handle_redaction_event(channel, client_msg_id, text)
    # Respond with the redacted text
    #say(f"Hello <@{user}>, you said: {text}. Redacted text: {text_redacted}. Stitched text: {stiched_text}")



@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    if "challenge" in data:
        print("Challenge accepted...returning now")
        return jsonify({'challenge': data['challenge']})
    return handler.handle(request)

def handle_redaction_event(channel_id, message_id, text):
    # Instantiate and use the PresidioTextRedactor class
    url = REDACTOR_URL + "redact_text/" 
    print("URL", url)
    headers = {"Content-Type": "application/json"}
    payload = {
            "channel_id": channel_id,
            "message_id": message_id,
            "text": text
            }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raise an error for bad status codes
    response_data = response.json()  # Parse JSON response
    print(response_data)

    return "", ""
    

if __name__ == "__main__":
    #SocketModeHandler(app, config["SLACK_BOT_TOKEN"]).start()
    flask_app.run(port=3000)



