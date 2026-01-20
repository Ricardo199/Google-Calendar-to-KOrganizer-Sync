import datetime
import os
import zoneinfo

from icalendar import Calendar, Event
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def main():
    creds= None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        
    try:
        service = build("calendar", "v3", credentials=creds)
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        print('Getting all events from the calendar')
        events_result=(
            service.events().list(
                calendarId="primary",
                timeMin=now,
                singleEvents=True,
                orderBy="startTime"
            ).execute()
        )
        events = events_result.get("items", [])
        cal = Calendar()
        for event in events:
            cal_event = Event()
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            cal_event.add('summary', event.get('summary', 'No Title'))
            cal_event.add('dtstart', datetime.datetime.fromisoformat(start).astimezone(zoneinfo.ZoneInfo("UTC")))
            cal_event.add('dtend', datetime.datetime.fromisoformat(end).astimezone(zoneinfo.ZoneInfo("UTC")))
            cal_event.add('description', event.get('description', ''))
            cal_event.add('location', event.get('location', ''))
            cal.add_component(cal_event)
        with open('calendar.ics', 'wb') as f:
            f.write(cal.to_ical())
    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    main()
    