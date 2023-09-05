from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os

def watch_gmail_inbox(service, user_id, topic_name):
    """
    Watches the Gmail inbox for the specified user and notifies the specified Pub/Sub topic.
    """
    request = {
        "labelIds": ["UNREAD"],
        "labelFilterAction": "include",
        "topicName": topic_name
    }
    try:
        return service.users().watch(userId=user_id, body=request).execute()
    except Exception as e:
        print(f"Error watching Gmail inbox: {e}")
        return None

def stop_gmail_watch(service, user_id):
    """
    Stops watching the Gmail inbox for the specified user.
    """
    try:
        return service.users().stop(userId=user_id).execute()
    except Exception as e:
        print(f"Error stopping Gmail watch: {e}")
        return None

def setup_gmail_api():
    """
    Sets up and returns the Gmail API service.
    """
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file('creds.json', SCOPES)
                creds = flow.run_local_server(port=8080)
            except Exception as e:
                print(f"Error setting up Gmail API: {e}")
                return None

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

if __name__ == "__main__":
    service = setup_gmail_api()
    if service:
        topic_name = 'projects/your project id/topics/topic name'
        watch_gmail_inbox(service, 'me', topic_name)
        print('Watch setup success!')
    else:
        print("Failed to set up Gmail API.")
