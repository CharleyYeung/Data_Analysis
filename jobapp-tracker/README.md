# Job Application Tracker

An intelligent job application tracking system that automatically monitors your Gmail inbox for job application updates, filters genuine opportunities, and extracts key information using AI.

## Overview

This tool helps job seekers manage multiple job applications by automatically:
- Scanning Gmail for job-related emails
- Using Google Gemini AI to intelligently distinguish genuine job updates from spam/unsolicited recruiter outreach
- Extracting company names and job titles
- Tracking application statuses
- Sending push notifications for new updates
- Storing data in CSV format (with optional AWS S3 backup)

## Features

 **Gmail Integration** - Securely connects to your Gmail account using OAuth2  
**Smart Email Filtering** - Distinguishes genuine job application responses from recruiter spam using Gemini AI  
**Intelligent Company Extraction** - Correctly identifies the actual hiring company even when emails come from job platforms like Indeed or LinkedIn  
**Automatic Data Collection** - Extracts company name, job title, and application status  
**CSV Export** - Saves all tracked applications to `job_alert.csv`  
**Push Notifications** - Get notified via ntfy.sh when new job updates arrive  
**Cloud Backup** - Optional AWS S3 integration for data persistence  

## Prerequisites

- Python 3.8+
- Gmail account with API access
- Google Gemini API key
- (Optional) AWS S3 bucket credentials
- (Optional) ntfy.sh account for notifications

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd jobapp-tracker
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### 1. Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Gmail API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download the credentials and save as `credentials.json` in the project root

### 2. Environment Variables

Create a `.env` file or set these environment variables:

```bash
GEMINI_API_KEY=your_gemini_api_key
NTFY_TOPIC_URL=https://ntfy.sh/your_topic_name  # Optional
AWS_S3_BUCKET=your_bucket_name  # Optional
AWS_ACCESS_KEY_ID=your_aws_key  # Optional
AWS_SECRET_ACCESS_KEY=your_aws_secret  # Optional
```

### 3. First-Time Setup

Run the script for the first time - it will prompt you to authorize Gmail access:
```bash
python main.py
```

A browser window will open for OAuth authentication. After authorizing, `token.json` will be created automatically.

## Usage

```bash
# Run the job tracker
python main.py
```

The script will:
1. Connect to your Gmail account
2. Search for job-related emails (customizable query)
3. Analyze each email with Gemini AI
4. Extract company and job details
5. Save results to `job_alert.csv`
6. Send notifications for new updates
7. Optionally backup data to AWS S3

## File Structure

```
jobapp-tracker/
├── main.py                 # Main application script
├── requirements.txt        # Python dependencies
├── credentials.json        # Gmail API credentials (OAuth2)
├── token.json             # Gmail API access token (auto-generated)
├── job_alert.csv          # Tracked job applications database
├── README.md              # This file
└── venv/                  # Virtual environment
```

## How It Works

### Email Analysis Flow

1. **Gmail Search** - The script queries Gmail for emails matching job-related keywords
2. **Gemini AI Filtering** - Each email is sent to Google Gemini for intelligent analysis:
   - Determines if it's a genuine job application update
   - Filters out unsolicited recruiter spam
   - Identifies emails from job application platforms (Indeed, LinkedIn, Glassdoor)
3. **Company Extraction** - For emails from job platforms, the AI extracts the actual hiring company name, not the platform name
4. **Data Storage** - Results are saved to CSV with the following structure:
   - Company Name
   - Job Title
   - Application Status
   - Email Date
   - Details

### CSV Output

The `job_alert.csv` file contains all tracked applications with extracted information for easy analysis and reference.

## Environment Variables Reference

| Variable | Purpose | Required |
|----------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini API key for email analysis | Yes |
| `NTFY_TOPIC_URL` | Notification topic URL for push alerts | No |
| `AWS_S3_BUCKET` | AWS S3 bucket for data backup | No |
| `AWS_ACCESS_KEY_ID` | AWS credentials for S3 access | No (if S3 used) |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials for S3 access | No (if S3 used) |

## Troubleshooting

### "credentials.json not found"
- Make sure you've downloaded the OAuth credentials from Google Cloud Console
- Place it in the project root directory

### "Invalid token"
- Delete `token.json` and run the script again to re-authenticate

### "GEMINI_API_KEY not set"
- Ensure your Gemini API key is properly set in environment variables
- The script will continue without it but with reduced filtering capability

### Gmail API quota exceeded
- The script respects Gmail API rate limits (50 messages per request by default)
- Wait before running again or upgrade your API quota

## Security Notes

- Never commit `credentials.json` or `token.json` to version control
- Add these files to `.gitignore`:
  ```
  credentials.json
  token.json
  .env
  ```
- Store API keys securely using environment variables or a secrets manager

## Dependencies

- `google-api-python-client` - Gmail API client
- `google-auth-oauthlib` - OAuth2 authentication
- `google-auth` - Google authentication library
- `boto3` - AWS S3 integration
- `requests` - HTTP requests for ntfy.sh notifications

## License

This project is provided as-is for personal use.

## Contributing

Feel free to fork, modify, and submit improvements!

## Support

For issues or questions, check the code comments or review the Gmail API and Gemini API documentation.
