"""Google Calendar to KOrganizer Sync Utility

This script fetches events from Google Calendar and creates an iCal file
that can be imported into KOrganizer or other calendar applications.

Requires:
    - Google Calendar API credentials (credentials.json)
    - Python packages: google-api-python-client, icalendar

Usage:
    python sync.py
"""

import datetime
import os
import zoneinfo
from typing import Optional, Dict, Any, List

from icalendar import Calendar, Event
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

# Define the scope for Google Calendar API access (read-only)
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class Parameters:
    """Configuration parameters for calendar synchronization.
    
    Attributes:
        calendarId: Google Calendar ID to sync from (default: 'primary')
        timeMin: Start time for fetching events (ISO format)
        orderBy: How to order events ('startTime' or 'updated')
    """
    calendarId: str = "primary"
    timeMin: str = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    orderBy: str = "startTime"


def authenticate() -> Optional[Credentials]:
    """Handle Google Calendar API authentication.
    
    Returns:
        Authenticated credentials or None if authentication fails
    """
    creds = None
    
    # Load existing credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds


def get_user_preferences() -> None:
    """Get user preferences for calendar sync parameters."""
    print('Getting all events from the calendar')
    print('What calendar do you want to sync?')
    Parameters.calendarId = input('Calendar ID (or press Enter for primary): ') or "primary"
    Parameters.timeMin = input('Start time (ISO format, or press Enter for now): ') or datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    Parameters.orderBy = input('Order by (startTime or updated, or press Enter for startTime): ') or "startTime"


def fetch_events(service) -> List[Dict[str, Any]]:
    """Fetch events from Google Calendar.
    
    Args:
        service: Authenticated Google Calendar service
        
    Returns:
        List of calendar events
    """
    events_result = service.events().list(
        calendarId=Parameters.calendarId,
        singleEvents=True,
        timeMin=Parameters.timeMin,
        orderBy=Parameters.orderBy
    ).execute()
    
    return events_result.get("items", [])


def create_ical_event(event: Dict[str, Any]) -> Event:
    """Convert Google Calendar event to iCal event.
    
    Args:
        event: Google Calendar event dictionary
        
    Returns:
        iCal Event object
    """
    cal_event = Event()
    
    # Extract start and end times (handle both datetime and date-only events)
    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['end'].get('date'))
    
    # Add event properties
    cal_event.add('summary', event.get('summary', 'No Title'))
    cal_event.add('dtstart', datetime.datetime.fromisoformat(start).astimezone(zoneinfo.ZoneInfo("UTC")))
    cal_event.add('dtend', datetime.datetime.fromisoformat(end).astimezone(zoneinfo.ZoneInfo("UTC")))
    cal_event.add('description', event.get('description', ''))
    cal_event.add('location', event.get('location', ''))
    
    return cal_event


def save_ical_file(events: List[Dict[str, Any]], filename: str = 'calendar.ics') -> None:
    """Save events to iCal file.
    
    Args:
        events: List of Google Calendar events
        filename: Output filename for iCal file
    """
    cal = Calendar()
    
    for event in events:
        cal_event = create_ical_event(event)
        cal.add_component(cal_event)
    
    with open(filename, 'wb') as f:
        f.write(cal.to_ical())
    
    print(f"Successfully created {filename} with {len(events)} events")


def open_ical_file(filename: str = 'calendar.ics') -> None:
    """Attempt to open the iCal file with the default application.
    
    Args:
        filename: iCal file to open
    """
    try:
        exit_code = os.system(f'xdg-open {filename} >/dev/null 2>&1 &')
        if exit_code != 0:
            print(f"Could not open {filename} automatically. Please open it manually.")
    except Exception as e:
        print(f"Could not open {filename} automatically: {e}")
    

def main() -> None:
    """Main function to authenticate and sync calendar events.
    
    Handles the complete workflow:
    1. Authenticate with Google Calendar API
    2. Get user preferences
    3. Fetch events from calendar
    4. Create and save iCal file
    5. Attempt to open the file
    """
    try:
        # Authenticate with Google Calendar API
        creds = authenticate()
        if not creds:
            print("Authentication failed")
            return
        
        # Build the Google Calendar service
        service = build("calendar", "v3", credentials=creds)
        
        # Get user preferences for sync
        get_user_preferences()
        
        # Fetch events from Google Calendar
        events = fetch_events(service)
        
        # Create and save iCal file
        save_ical_file(events)
        
        # Try to open the file automatically
        open_ical_file()
        
    except HttpError as error:
        print(f"An error occurred while accessing Google Calendar: {error}")
    except FileNotFoundError:
        print("credentials.json not found. Please set up Google Calendar API credentials.")
    except Exception as error:
        print(f"An unexpected error occurred: {error}")

if __name__ == '__main__':
    main()