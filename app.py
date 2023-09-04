import os
import json
import logging
import re
import base64
from flask import Flask, request, jsonify
from flask_config import Config

from bs4 import BeautifulSoup
import requests

from discord import SyncWebhook
from datetime import datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


from firebaser import FirebaseController

# Initialize logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config.from_object(Config)


class GmailAPI:
    @staticmethod
    def setup():
        """Setup and return the Gmail API service."""
        SCOPES = app.config['GMAIL_SCOPES']
        creds = None
        
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json')

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('creds.json', SCOPES)
                creds = flow.run_local_server(port=8080)

            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)
    
    @staticmethod
    def get_messages(service, history_id):
        messages = []

        try:
            histories = service.users().history().list(userId='me', startHistoryId=history_id).execute()
        except Exception as e:
            logging.error(f"Error fetching histories: {e}")
            return messages

        if histories and 'history' in histories:
            for history in (history for history in histories['history'] if 'messages' in history):
                for message in history['messages']:
                    try:
                        message_data = service.users().messages().get(userId='me', id=message['id']).execute()
                        messages.append(message_data)
                    except Exception as e:
                        logging.error(f"Error fetching message details: {e}")

        return messages


class DiscordNotifier:
    @staticmethod
    def send_msg(data, attachment=False):
        """Send a message to Discord"""
        webhook_url = app.config['DISCORD_WEBHOOK_URL']
        try:
            if attachment:
                with open(data.get('filename'), 'rb') as f:
                    files = {
                        "file": (data.get('filename').split("/")[-1], f)
                    }
                    
                    payload = {}
                    if 'message' in data:
                        payload["content"] = data.get('message')
                    
                    response = requests.post(webhook_url, data=payload, files=files)
                    if response.status_code == 200:
                        os.remove(data.get('filename'))  # Delete the file after sending.
                        return True
                    
            else:
                webhook = SyncWebhook.from_url(webhook_url)
                webhook.send(data.get('message'))
            
            return True
        except:
            logging.error('Error while sending message to Discord.')
            return False


class EmailProcessor:
    @staticmethod
    def extract_details(message, service):
        """Extracts the email details."""
        message_id = message.get('id', '')
        email_details = {
            "From": "",
            "To": "",
            "Subject": "",
            "Date": "",
            "PlainTextBody": "",
            "HTMLBody": "",
            "AlternativeBody": "",
            "attachment": False,
            "filename": None
        }

        headers = message.get('payload', {}).get('headers', [])

        for header in headers:
            name = header.get('name')
            if name == "From":
                email_details["From"] = header.get('value')
            elif name == "To":
                email_details["To"] = header.get('value')
            elif name == "Subject":
                email_details["Subject"] = header.get('value')
            elif name == "Date":
                email_details["Date"] = header.get('value')

        # Extract the body
        parts = message.get('payload', {}).get('parts', [])
        for part in parts:
            if part.get('mimeType') == "text/plain":
                encoded_body_data = part.get('body', {}).get('data')
                if encoded_body_data:
                    decoded_body = base64.urlsafe_b64decode(encoded_body_data).decode('utf-8')
                    email_details["PlainTextBody"] = decoded_body
            elif part.get('mimeType') == "text/html":
                encoded_body_data = part.get('body', {}).get('data')
                if encoded_body_data:
                    decoded_body = base64.urlsafe_b64decode(encoded_body_data).decode('utf-8')
                    email_details["HTMLBody"] = decoded_body
            elif part.get('mimeType') == "multipart/alternative":
                inner_parts = part.get('parts', [])
                encoded_body_data = inner_parts[0].get('body', {}).get('data') if len(inner_parts) > 0 else None
                if encoded_body_data:
                    decoded_body = base64.urlsafe_b64decode(encoded_body_data).decode('utf-8')
                    email_details["AlternativeBody"] = decoded_body
            elif part.get('mimeType') == "text/csv":
                try:
                    filename = part.get('filename')
                    attachmentId = part.get('body', {}).get('attachmentId')
                    encoded_attached_data = service.users().messages().attachments().get(userId='me', messageId=message_id, id=attachmentId).execute()['data']
                    decoded_content = base64.urlsafe_b64decode(encoded_attached_data)
                    if decoded_content:
                        with open(filename, 'wb') as file:
                            file.write(decoded_content)
                        email_details['attachment'] = True
                        email_details['filename'] = filename
                except:
                    pass

        return email_details

    @staticmethod
    def format_details(details):
        """Formats the email details."""
        parsed_html_text = BeautifulSoup(details.get('HTMLBody', ''), 'html.parser').get_text(separator=' ')
        parsed_text = re.sub(r'\s+', ' ', parsed_html_text).strip()
        
        plain_text = details.get('PlainTextBody', '').strip()
        
        if parsed_text == plain_text:
            body = parsed_text
        else:
            body = plain_text + '\n' + parsed_text
        
        conj = '\n' if body != '' else ''
        body = body + conj + details.get('AlternativeBody', '')

        formatted_string = (
        f"@everyone\n{15*'-'}\n"
            f"Date: {details['Date']}\n"
            f"From: {details['From']}\n"
            f"To: {details['To']}\n"
            f"Subject: {details['Subject']}\n"
            f"Body: {body}\n{15*'-'}\n"
        )
        return formatted_string


class FirebaseDB:
    def __init__(self):
        self.controller = FirebaseController()

    def authorize(self):
        """Authorize the Firebase client."""
        self.controller.authorize_with_email(
            app.config['FIREBASE_EMAIL'], app.config['FIREBASE_PASSWORD'])

    def get_history_id(self):
        """Retrieve the history ID."""
        return self.controller.get_history_id()

    def set_history_id(self, history_id):
        """Set the history ID."""
        self.controller.set_history_id(str(history_id))

    def is_email_sent(self, msg_id):
        """Check if the email is already sent."""
        return self.controller.is_email_sent(msg_id)

    def save_email(self, log_entry):
        """Save the email data."""
        self.controller.save_email(log_entry)


@app.route('/webhook', methods=['POST'])
def webhook():
    logging.info("Webhook received with data: %s", request.json)

    db = FirebaseDB()
    db.authorize()

    encoded_data = request.json['message']['data']
    decoded_data = base64.b64decode(encoded_data).decode('utf-8')
    data_json = json.loads(decoded_data)

    email_address = data_json['emailAddress']
    history_id = data_json['historyId']

    prev_history_id = db.get_history_id()

    if history_id and prev_history_id:
        service = GmailAPI.setup()
        email_details = GmailAPI.get_messages(service, prev_history_id)

        for detail in email_details:
            msg_id = detail.get("id")

            if db.is_email_sent(msg_id):
                logging.info(f"Message {msg_id} already processed. Skipping...")
                continue

            extracted_details = EmailProcessor.extract_details(detail, service)
            formatted_email = EmailProcessor.format_details(extracted_details)

            if DiscordNotifier.send_msg({'message': formatted_email, 'filename': extracted_details.get('filename')}, extracted_details.get('attachment')):
                logging.info('Message sent to Discord')
                db.save_email({"msg_id": msg_id, "timestamp": datetime.utcnow().isoformat()})
            else:
                logging.error('Failed to send message to Discord')

        db.set_history_id(history_id)

    return jsonify({'status': 'success'}), 200


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], port=app.config['PORT'], host="0.0.0.0")
