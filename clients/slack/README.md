## SLACK CLIENT
The code to interface with the slack client


### Initial Dev Setup
1.) Make sure you have the following `.env`: SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET. 
- To get the signing secret - please go to this (link)[https://api.slack.com/apps/A0780FMFZGV/general?] and scroll down to credentials to find signing secret section.
- To get the slack bot token - please go to this (link)[https://api.slack.com/apps/A0780FMFZGV/general?] and scroll down to the tokens section to find it.

2.) Download `ngrok`
- `$foo: brew install ngrok/ngrok/ngrok`
- `$foo: ngro http 3000`
- Copy the https url. An example is `https://e402-2603-3024-1cd7-a100-6406-f095-cd0a-11c1.ngrok-free.app/slack/events`
- Go to this (link)[https://api.slack.com/apps/A0780FMFZGV/event-subscriptions?success=1]. Copy and paste the ngrok https url. It should fail.
- Run `app.py` and then check again the challenge request. This should work. 
