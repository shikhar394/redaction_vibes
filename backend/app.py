from flask import Flask, request, jsonify
from ml_services.presidio_redactor import PresidioTextRedactor
import os
from supabase import create_client, Client
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()



app = Flask(__name__)
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


@app.route('/redact_text/', methods=['POST'])
def redact_text():
    data = request.get_json()
    text = data['text']
    message_id = data['message_id']
    channel_id = data['channel_id']

    redactor = PresidioTextRedactor(text)
    redacted_text = redactor.redact()

    data, count = supabase.table('message_pii').insert(
        {
            "pii_type": redactor.redacted_tokens, 
            "message_id": message_id,
            "channel_id": channel_id
        }
    ).execute()

    return jsonify({
        'redacted_text': redacted_text,
        'redacted_tokens': redactor.redacted_tokens
    })

if __name__ == '__main__':
    app.run(debug=True)


