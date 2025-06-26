import os
from datetime import datetime, timezone, timedelta
import pickle
import json
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64

# Constants
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
HOLIDAY_CALENDAR_ID = 'en.indian#holiday@group.v.calendar.google.com'
CACHE_FILE = 'upcoming_holidays.json'

def get_credentials():
    creds = None
    token_path = 'token.pickle'

    if not os.path.exists(token_path):
        with open('token.pickle.b64', 'rb') as f:
            encoded = f.read()
        with open(token_path, 'wb') as f:
            f.write(base64.b64decode(encoded))

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(json.loads(os.environ['GOOGLE_CLIENT_SECRET_JSON']), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return creds

def fetch_upcoming_holidays():
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)

    now = datetime.now(timezone.utc).isoformat()
    end = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()

    events_result = (
        service.events()
        .list(
            calendarId=HOLIDAY_CALENDAR_ID,
            timeMin=now,
            timeMax=end,
            singleEvents=True,
            orderBy='startTime',
        )
        .execute()
    )

    events = events_result.get('items', [])
    holidays = []
    for event in events:
        start = event['start'].get('date')
        summary = event.get('summary')
        if start and summary:
            holidays.append((start, summary))
    return holidays

def is_cache_stale():
    if not os.path.exists(CACHE_FILE):
        return True
    try:
        modified_time = datetime.fromtimestamp(os.path.getmtime(CACHE_FILE))
        return (datetime.now() - modified_time) > timedelta(hours=24)
    except Exception:
        return True

def check_and_update_cache():
    if is_cache_stale():
        print("🕒 Holiday cache is stale. Updating...")
        holidays = fetch_upcoming_holidays()
        with open(CACHE_FILE, "w") as f:
            json.dump(holidays, f)
        print("✅ Holiday cache updated.")
    else:
        print("📁 Holiday cache is fresh.")

if __name__ == '__main__':
    check_and_update_cache()
    with open(CACHE_FILE) as f:
        holidays = json.load(f)
        for date, name in holidays:
            print(f"{date} - {name}")