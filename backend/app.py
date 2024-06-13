from flask import Flask, request, jsonify
from ml_services.presidio_redactor import PresidioTextRedactor

app = Flask(__name__)

@app.route('/redact_text/', methods=['POST'])
def redact_text():
    data = request.get_json()
    text = data['text']
    redactor = PresidioTextRedactor(text)
    redacted_text = redactor.redact()
    
    return jsonify({
        'redacted_text': redacted_text,
        'redacted_tokens': redactor.redacted_tokens
    })

if __name__ == '__main__':
    app.run(debug=True)
