from flask import Flask, request, jsonify
import os
from flask_cors import CORS
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)
CORS(app)

# API keys & environment variables
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
API_KEY = os.getenv("API_KEY")
FROM_EMAIL = os.getenv("EMAIL_ADDRESS")

# Email template with placeholders
EMAIL_TEMPLATE = """
Dear {client_name},

Greetings from Axion Labs!

We are pleased to formalize our agreement regarding the project "{project_name}".

As per the agreement:
- We will deliver the project according to the timelines discussed.
- While we take all reasonable steps to meet deadlines, we cannot guarantee against unforeseen technical issues or delays.
- Once the maintenance plan ends or if the client opts out, all liability is handed over to the client, and we assume no further responsibility.
- Maintenance plans may be renewed at any time upon agreement.

We look forward to working with you and ensuring the success of "{project_name}".

Best Regards,
Axion Labs
"""

@app.route("/home", methods=["GET"])
def home():
    return jsonify({"status": "success", "message": "Hello world"}), 200

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/send-email", methods=["POST"])
def send_email():
    try:
        # Check API key
        key = request.headers.get("x-api-key")
        if key != API_KEY:
            return jsonify({"status": "error", "message": "Unauthorized"}), 401

        # Get JSON data
        data = request.json
        to_email = data.get("to_email")
        client_name = data.get("client_name")
        project_name = data.get("project_name")

        if not all([to_email, client_name, project_name]):
            return jsonify({"status": "error", "message": "Missing fields"}), 400

        # Prepare email body
        body = EMAIL_TEMPLATE.format(client_name=client_name, project_name=project_name)

        # Create SendGrid message
        message = Mail(
            from_email=os.getenv("EMAIL_ADDRESS"),
            to_emails=to_email,
            subject=f"Official Agreement for {project_name}",
            plain_text_content=body
        )

        # Send via SendGrid API
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        if 200 <= response.status_code < 300:
            return jsonify({"status": "success", "message": f"Email sent to {to_email}"}), 200
        else:
            return jsonify({"status": "error", "message": f"SendGrid error: {response.status_code}"}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
