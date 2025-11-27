from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# Gmail SMTP configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
API_KEY = os.getenv("API_KEY")

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

        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = f"Official Agreement for {project_name}"
        body = EMAIL_TEMPLATE.format(client_name=client_name, project_name=project_name)
        msg.attach(MIMEText(body, 'plain'))

        # Send email via Gmail SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        return jsonify({"status": "success", "message": f"Email sent to {to_email}"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
