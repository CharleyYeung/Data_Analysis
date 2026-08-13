import os
import csv
import json
from datetime import datetime, timedelta
import requests
import boto3
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from botocore.exceptions import ClientError
import time

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

NTFY_TOPIC_URL = os.environ.get('NTFY_TOPIC_URL')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET')
CSV_FILE_NAME = 'job_alert.csv'

def get_gmail_service():
    """
    Authenticate and build the Gmail API service using token.json.
    """
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

def search_emails(service, query):
    """
    Search Gmail messages based on the given query string.
    """
    try:
        result = service.users().messages().list(userId='me', q=query, maxResults=50).execute()
        return result.get('messages', [])
    except HttpError as error:
        print(f'An error occurred during email search: {error}')
        return []

def get_email_details(service, msg_id):
    """
    Retrieve full details of a specific email message by ID.
    """
    try:
        message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        return message
    except HttpError as error:
        print(f'An error occurred while fetching email details: {error}')
        return None

def send_notification(title, body):
    """
    Send push notifications using ntfy.sh.
    """
    if not NTFY_TOPIC_URL:
        return
    try:
        requests.post(
            NTFY_TOPIC_URL,
            data=body.encode(encoding='utf-8'),
            headers={"Title": title, "Tags": "briefcase"}
        )
    except Exception as e:
        print(f"Error sending ntfy notification: {e}")

def analyze_email_with_gemini(sender, subject, snippet):
    """
    Query Gemini via REST API to intelligently filter and extract job application details.
    """
    if not GEMINI_API_KEY:
        print("GEMINI_API_KEY not set.")
        return {"is_genuine": True, "company": "Unknown Company", "job_title": subject, "status": "Update Received"}

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-3.1-flash-lite:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
You are an expert AI assistant helping a job seeker track their job applications.
Analyze the following email details carefully:
- Sender: {sender}
- Subject: {subject}
- Snippet: {snippet}

Task:
1. Determine if this email is a **genuine job application update or response** for a position the user actively applied for, OR an active interview/assessment communication they are participating in.
2. **Strictly filter out (return `is_genuine: false`)**:
   - Unsolicited cold outreach from recruiters or agencies pitching random jobs the user never applied for.
   - General promotional newsletters, mass job board broadcasts (e.g., generic LinkedIn/Glassdoor job recommendation digests).
3. If it is genuine, extract the **real hiring company or recruiter agency name**. 
   - *Important rule for job platforms*: If the email is an application confirmation or alert from a job board platform like **Indeed**, **LinkedIn**, or **Glassdoor**, look inside the subject or snippet to find the **actual underlying hiring employer** (e.g., if it says "Indeed Application: Data Analyst Intern at Gradence", the company is **Gradence**, NOT Indeed). Never use the platform name as the company name.
4. Extract the clean **job title**.
5. Categorize the status into one of these exact values: ["Applied", "Interview / Assessment", "Offer 🎉", "Rejected", "Update Received"].

Return your answer strictly in the following JSON format:
{{
  "is_genuine": true or false,
  "company": "Extracted Company Name",
  "job_title": "Extracted Clean Job Title",
  "status": "Applied / Interview / Assessment / Offer / Rejected / Update Received"
}}
"""

    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 503:
                sleep_time = (2 ** attempt) + 1
                print(f" [⚠️ Server temporarily busy (503), retrying {attempt + 1}/{max_retries}, waiting {sleep_time}s...] ")
                time.sleep(sleep_time)
                continue
                
            response.raise_for_status()
            result_json = response.json()
            
            raw_text = result_json['candidates'][0]['content']['parts'][0]['text'].strip()
            
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                return data
            else:
                return {"is_genuine": True, "company": "Unknown Company", "job_title": subject, "status": "Update Received"}
                
        except requests.exceptions.HTTPError as e:
            print(f" [⚠️ HTTP Error] {e}")
            if e.response is not None:
                print(f" [⚠️ Google Server Details] {e.response.text}")
            break
        except Exception as e:
            print(f" [⚠️ Other Error] {e}")
            break

    return {"is_genuine": True, "company": "Unknown Company", "job_title": subject, "status": "Update Received"}

def download_from_s3(file_name, bucket):
    """
    Download the existing CSV tracker from S3 at startup to preserve history.
    """
    if not bucket:
        return
    s3_client = boto3.client('s3')
    try:
        s3_client.download_file(bucket, os.path.basename(file_name), file_name)
        print(f"Successfully downloaded {file_name} from S3.")
    except ClientError as e:
        print(f"S3 download note (file may not exist yet): {e}")

def upload_to_s3(file_name, bucket):
    """
    Upload the updated CSV tracker to S3 and generate a presigned download URL.
    """
    if not bucket:
        return None
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_name, bucket, os.path.basename(file_name))
        url = s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': os.path.basename(file_name)}, ExpiresIn=900)
        return url
    except ClientError as e:
        print(f"S3 Error: {e}")
        return None

def main():
    service = get_gmail_service()
    if not service:
        return

    # Download existing state from S3 before processing
    download_from_s3(CSV_FILE_NAME, AWS_S3_BUCKET)

    # Search for emails received within the past 2 hours to capture new updates safely
    search_terms = '(application OR interview OR assessment OR recruitment OR status OR hiring OR position OR candidate)'
    two_hours_ago_timestamp = int((datetime.now() - timedelta(hours=2)).timestamp())
    query = f'{search_terms} after:{two_hours_ago_timestamp}'
    
    print(f"Searching for emails with query: {query}")
    messages = search_emails(service, query)

    if not messages:
        print("No new emails found in the past hour.")
        return

    print(f"Found {len(messages)} email(s) to inspect.")

    rows = []
    fieldnames = ['Company', 'Job Title', 'Application Date', 'Status', 'Last Updated', 'Subject', 'Snippet']
    
    if os.path.exists(CSV_FILE_NAME):
        with open(CSV_FILE_NAME, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)

    new_updates_count = 0

    for msg_summary in messages:
        msg_details = get_email_details(service, msg_summary['id'])
        if not msg_details:
            continue

        headers = msg_details['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
        snippet = msg_details['snippet']

        # Analyze email with Gemini AI
        ai_result = analyze_email_with_gemini(sender, subject, snippet)
        
        # Pause for 4 seconds to respect the free tier rate limit (15 requests per minute)
        time.sleep(4)
        
        if not ai_result.get("is_genuine", False):
            print(f"Skipping filtered email via Gemini: {subject}")
            continue

        company = ai_result.get("company", "Unknown Company")
        job_title = ai_result.get("job_title", subject)
        status = ai_result.get("status", "Update Received")
        today_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print(f"\n[Gemini Processed] Company: {company} | Role: {job_title} | Status: {status}")

        # Update existing record or append new one
        found_match = False
        for row in rows:
            if row['Company'].strip().lower() == company.strip().lower() and \
               row['Job Title'].strip().lower() == job_title.strip().lower():
                row['Status'] = status
                row['Last Updated'] = today_str
                row['Subject'] = subject
                row['Snippet'] = snippet
                found_match = True
                break

        if not found_match:
            new_row = {
                'Company': company,
                'Job Title': job_title,
                'Application Date': today_str.split()[0],
                'Status': status,
                'Last Updated': today_str,
                'Subject': subject,
                'Snippet': snippet
            }
            rows.append(new_row)

        new_updates_count += 1

    # Write back to local CSV
    with open(CSV_FILE_NAME, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSuccessfully updated {CSV_FILE_NAME} with {new_updates_count} record(s).")

    # Upload updated CSV to S3 and notify via ntfy if new updates exist
    presigned_url = upload_to_s3(CSV_FILE_NAME, AWS_S3_BUCKET)
    if new_updates_count > 0:
        body = f"Processed {new_updates_count} job application update(s)."
        if presigned_url:
            body += f"\n\nView updated tracker (expires in 15 mins):\n{presigned_url}"
        send_notification("Job Tracker Updated", body)

if __name__ == '__main__':
    main()