import os
import sys
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request, jsonify
from dotenv import dotenv_values

# Add the parent directory of ml_services to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
from ml_services.presidio_redactor import PresidioTextRedactor

#----------------INIT TOKENS------------------------#
config = dotenv_values(".env")  # config = {"SLACK_BOT_TOKEN": "foo", "SLACK_SIGNING_SECRET": "fi"}
if not config["SLACK_BOT_TOKEN"] or not config["SLACK_SIGNING_SECRET"]:
    raise ValueError("Missing SLACK_BOT_TOKEN or SLACK_SIGNING_SECRET")

#--------------INIT MODULES-----------#
# Install the Slack app and get xoxb- token in advance
app = App(token=config["SLACK_BOT_TOKEN"], signing_secret=config["SLACK_SIGNING_SECRET"])

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
    text = event.get('text')
    channel = event.get('channel')
    print(f"Message from {user} in channel {channel}: {text}")
    text_redacted, stiched_text = handle_redaction_event(text)
    # Respond with the redacted text
    say(f"Hello <@{user}>, you said: {text}. Redacted text: {text_redacted}. Stitched text: {stiched_text}")



@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    if "challenge" in data:
        print("Challenge accepted...returning now")
        return jsonify({'challenge': data['challenge']})
    return handler.handle(request)

def handle_redaction_event(text):
    # Instantiate and use the PresidioTextRedactor class
    redactor = PresidioTextRedactor(text)
    text_redacted = redactor.redact()
    stiched_text = redactor.stitch()
    return text_redacted, stiched_text
    

if __name__ == "__main__":
    #SocketModeHandler(app, config["SLACK_BOT_TOKEN"]).start()
    flask_app.run(port=3000)



