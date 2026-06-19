from __future__ import print_function

import os.path
from datetime import datetime, timedelta
import csv

import requests
import boto3
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from botocore.exceptions import ClientError


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# --- Configuration ---
# Keywords to search for in emails. This will find emails containing any of these phrases.
SEARCH_KEYWORDS = ' OR '.join(['"application received"', '"coding challenge"', 'interview', 'assessment', 'next steps', 'offer', 'rejection'])

# The topic URL for ntfy notifications. We'll use a GitHub secret for this.
NTFY_TOPIC_URL = os.environ.get('NTFY_TOPIC_URL')

# --- AWS S3 Configuration ---
AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET')
# AWS credentials will be read automatically by boto3 from the environment variables
# set in the GitHub Actions workflow.
CSV_FILE_NAME = 'job_alert.csv'

def get_gmail_service():
    """Authenticates with the Gmail API and returns a service object."""
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        print("Successfully connected to Gmail API.")
        return service
    except HttpError as error:
        print(f'An error occurred while building the service: {error}')
        return None

def search_emails(service, query):
    """Searches for emails matching the given query."""
    try:
        result = service.users().messages().list(userId='me', q=query).execute()
        return result.get('messages', [])
    except HttpError as error:
        print(f'An error occurred during email search: {error}')
        return []

def get_email_details(service, msg_id):
    """Fetches the full details of a specific email."""
    try:
        message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        return message
    except HttpError as error:
        print(f'An error occurred while fetching email details: {error}')
        return None

def send_notification(title, body):
    """Sends a push notification via ntfy."""
    if not NTFY_TOPIC_URL:
        print("NTFY_TOPIC_URL not set. Skipping notification.")
        return
    try:
        response = requests.post(
            NTFY_TOPIC_URL,
            data=body.encode(encoding='utf-8'),
            headers={
                "Title": title,
                "Tags": "briefcase" # Adds a briefcase icon to the notification
            }
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        print("Notification sent successfully via ntfy.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending ntfy notification: {e}")

def upload_to_s3(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket."""
    if not bucket:
        print("AWS_S3_BUCKET not set. Skipping S3 upload.")
        return False
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        print(f"File {file_name} uploaded to {bucket}/{object_name}.")
        # Generate a presigned URL that expires in 15 minutes (900 seconds)
        url = s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': object_name}, ExpiresIn=900)
        return url
    except ClientError as e:
        print(f"Error uploading file to S3: {e}")
        return None

def main():
    """The main function to run the job application monitoring script."""
    service = get_gmail_service()
    if not service:
        return

    # To meet the cron job requirement, we search for emails from the last hour.
    one_hour_ago = (datetime.now() - timedelta(hours=1)).strftime('%Y/%m/%d %H:%M')
    query = f'({SEARCH_KEYWORDS}) after:{one_hour_ago}'

    print(f"Searching for emails with query: {query}")
    messages = search_emails(service, query)

    if not messages:
        print("No new job application updates found in the last hour.")
    else:
        print(f"Found {len(messages)} new email(s).")

        # Check if the CSV file exists to determine if we need to write headers
        csv_file_exists = os.path.exists(CSV_FILE_NAME)

        with open(CSV_FILE_NAME, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write header only if the file is new
            if not csv_file_exists:
                writer.writerow(['Timestamp', 'Sender', 'Subject', 'Snippet'])

            for msg_summary in messages:
                msg_details = get_email_details(service, msg_summary['id'])
                if not msg_details:
                    continue

                headers = msg_details['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                snippet = msg_details['snippet']

                print(f"\n--- New Update ---")
                print(f"From: {sender}")
                print(f"Subject: {subject}")
                print(f"Snippet: {snippet}")

                # Write data to CSV
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                writer.writerow([timestamp, sender, subject, snippet])

                # We'll send one summary notification at the end

        # After processing all messages, upload the updated CSV to S3
        presigned_url = upload_to_s3(CSV_FILE_NAME, AWS_S3_BUCKET)

        # Send one notification with a link to the CSV
        notification_body = f"Found {len(messages)} new job update(s)."
        if presigned_url:
            notification_body += f"\n\nView the updated list here (link expires in 15 mins):\n{presigned_url}"
        send_notification("Job Application Summary", notification_body)

if __name__ == '__main__':
    main()