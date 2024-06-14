import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request, jsonify
from dotenv import dotenv_values

#----------------INIT TOKENS------------------------#
config = dotenv_values(".env")  # config = {"SLACK_APP_TOKEN": "foo", "SLACK_SIGNING_SECRET": "fi"}
if not config["SLACK_BOT_TOKEN"] or not config["SLACK_SIGNING_SECRET"]:
    raise ValueError("Missing SLACK_BOT_TOKEN or SLACK_SIGNING_SECRET")

#--------------INIT MODULES-----------#
# Install the Slack app and get xoxb- token in advance
#app = App(token=os.environ["SLACK_BOT_TOKEN"])
app = App(token=config["SLACK_BOT_TOKEN"], signing_secret=config["SLACK_SIGNING_SECRET"])

# Flask web server for the Slack events
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)
logging.basicConfig(level=logging.DEBUG)


#-----------INIT FUNCTIONS---------------#
# Listens to incoming messages
@app.event("message")
def handle_message_events(event, say):
    user = event['user']
    text = event['text']
    channel = event['channel']
    print(f"Message from {user} in channel {channel}: {text}")

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    if "challenge" in data:
        return jsonify({'challenge': data['challenge']})
    return handler.handle(request)


if __name__ == "__main__":
    #SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
    #SocketModeHandler(app, SLACK_APP_TOKEN).start()
    flask_app.run(port=3000)



