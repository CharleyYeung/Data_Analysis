import os
import base64
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def test_search_past_month():
    service = get_gmail_service()
    
    # Calculate the date one month ago in the format YYYY/MM/DD
    one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y/%m/%d')
    

    keywords = '("application received" OR "coding challenge" OR interview OR assessment OR next steps OR offer OR rejection OR application)'
    
    #  Filter emails from the past month with the specified keywords
    query = f'{keywords} after:{one_month_ago}'
    
    print(f"Searching for emails from the past month with the following Query: {query}\n")
    print("-" * 50)
    
    # 呼叫 Gmail API
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    
    if not messages:
        print("Cannot find any emails matching the criteria in the past month.")
        return

    print(f"✅ Message Found: {len(messages)} Emails：\n")
    
    for msg in messages:
        msg_id = msg['id']
        msg_data = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        
        # Retrieve (Header)
        headers = msg_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Subject not found')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '無Sender')
        date_str = next((h['value'] for h in headers if h['name'] == 'Date'), 'Date not found')
        
        print(f"📌 Sender: {sender}")
        print(f"📌 Subject: {subject}")
        print(f"📌 Date: {date_str}")
        print("-" * 30)

if __name__ == '__main__':
    test_search_past_month()