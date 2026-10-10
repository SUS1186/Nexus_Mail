import base64
import os
import re
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose'
]

class GmailService:
    def __init__(self, token_path: str = 'token.json', credentials_path: str = 'credentials.json'):
        self.token_path = token_path
        self.credentials_path = credentials_path
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        return build('gmail', 'v1', credentials=creds)

    def _clean_text(self, text: str) -> str:
        """Removes duplicate whitespace and excess line breaks."""
        text = re.sub(r'\r\n|\r|\n', '\n', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()

    def _extract_body_from_payload(self, payload: dict) -> str:
        """Recursively traverses MIME parts to extract plain text or converted HTML."""
        # Case 1: Payload has data directly
        if 'data' in payload.get('body', {}):
            raw_data = payload['body']['data']
            decoded = base64.urlsafe_b64decode(raw_data).decode('utf-8', errors='ignore')
            if payload.get('mimeType') == 'text/html':
                soup = BeautifulSoup(decoded, 'html.parser')
                return soup.get_text(separator=' ')
            return decoded

        # Case 2: Multipart payload
        parts = payload.get('parts', [])
        for part in parts:
            mime_type = part.get('mimeType', '')
            if mime_type == 'text/plain' and 'data' in part.get('body', {}):
                raw_data = part['body']['data']
                return base64.urlsafe_b64decode(raw_data).decode('utf-8', errors='ignore')
            elif mime_type == 'text/html' and 'data' in part.get('body', {}):
                raw_data = part['body']['data']
                decoded = base64.urlsafe_b64decode(raw_data).decode('utf-8', errors='ignore')
                soup = BeautifulSoup(decoded, 'html.parser')
                return soup.get_text(separator=' ')
            elif 'parts' in part:
                nested = self._extract_body_from_payload(part)
                if nested:
                    return nested

        return ""

    def fetch_emails(self, max_results: int = 50, query: str = None) -> list[dict]:
        """
        Fetches emails from inbox.
        Example queries:
          query="before:2026/01/01"       -> emails older than Jan 1, 2026
          query="older_than:1m"           -> emails older than 1 month
          query="from:github.com"         -> specific sender
        """
        params = {'userId': 'me', 'maxResults': max_results}
        if query:
            params['q'] = query

        results = self.service.users().messages().list(**params).execute()
        messages = results.get('messages', [])
        parsed_emails = []

        for item in messages:
            msg = self.service.users().messages().get(userId='me', id=item['id'], format='full').execute()
            headers = {h['name'].lower(): h['value'] for h in msg.get('payload', {}).get('headers', [])}
            
            raw_body = self._extract_body_from_payload(msg.get('payload', {}))
            cleaned_body = self._clean_text(raw_body)

            parsed_emails.append({
                "message_id": msg['id'],
                "thread_id": msg.get('threadId', msg['id']),
                "sender": headers.get('from', 'Unknown'),
                "subject": headers.get('subject', '(No Subject)'),
                "date": headers.get('date', ''),
                "snippet": msg.get('snippet', ''),
                "body": cleaned_body
            })

        return parsed_emails

    def create_draft(self, to: str, subject: str, body: str, thread_id: str = None) -> dict:
        """Creates a real email draft in the user's Gmail inbox."""
        import email.message

        message = email.message.EmailMessage()
        message.set_content(body)
        message['To'] = to
        message['Subject'] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        draft_body = {'message': {'raw': encoded_message}}

        if thread_id:
            draft_body['message']['threadId'] = thread_id

        return self.service.users().drafts().create(userId='me', body=draft_body).execute()

        return parsed_emails