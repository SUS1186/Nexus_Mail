import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Read-only scope is sufficient for fetching emails
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    # token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no valid credentials, trigger the browser login flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for future runs
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def fetch_latest_email():
    print("Connecting to Gmail API...")
    service = get_gmail_service()
    
    # Query the most recent message in the inbox
    results = service.users().messages().list(userId='me', maxResults=1).execute()
    messages = results.get('messages', [])

    if not messages:
        print("Inbox is empty or no messages found.")
        return

    # Fetch full message details
    msg_id = messages[0]['id']
    msg = service.users().messages().get(userId='me', id=msg_id).execute()
    headers = msg['payload']['headers']
    
    subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '(No Subject)')
    sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '(Unknown Sender)')
    snippet = msg.get('snippet', '')

    print("\n--- Message Fetched Successfully ---")
    print(f"ID:      {msg_id}")
    print(f"From:    {sender}")
    print(f"Subject: {subject}")
    print(f"Snippet: {snippet}")
    print("------------------------------------")

if __name__ == '__main__':
    fetch_latest_email()