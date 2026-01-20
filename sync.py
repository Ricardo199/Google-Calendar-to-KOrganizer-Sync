"""Google Calendar to KOrganizer Sync Utility

This script fetches events from Google Calendar and creates an iCal file
that can be imported into KOrganizer or other calendar applications.
"""

import datetime
import os
import zoneinfo
import subprocess

from icalendar import Calendar, Event
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

# Define the scope for Google Calendar API access (read-only)
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class Parameters:
    """Class to hold parameters for synchronization."""
    calendarId: str = "primary"  # Default to the primary calendar
    timeMin: str = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()  # Current time in UTC
    orderBy: str = "startTime"  # Order events by start time
    
    

def main():
    """Main function to authenticate and sync calendar events."""
    # Initialize credentials variable
    creds = None
    
    # Check if we have saved credentials from a previous run
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If credentials don't exist or are invalid, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired credentials
            creds.refresh(Request())
        else:
            # Run OAuth flow to get new credentials
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        
    try:
        # Build the Google Calendar service
        service = build("calendar", "v3", credentials=creds)
        
        # Get current time in UTC for fetching upcoming events
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        
        print('Getting all events from the calendar')
        print('What calendar do you want to sync?')
        Parameters.calendarId = input('Calendar ID (or press Enter for primary): ') or "primary"
        Parameters.timeMin = input('Start time (ISO format, or press Enter for now): ') or datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        Parameters.orderBy = input('Order by (startTime or updated, or press Enter for startTime): ') or "startTime"
        
        # Fetch upcoming events from the primary calendar
        events_result = (
            service.events().list(
                calendarId=Parameters.calendarId,      # Use the user's primary calendar
                singleEvents=True,                     # Expand recurring events into individual instances
                timeMin=Parameters.timeMin,            # Fetch events starting from now
                orderBy=Parameters.orderBy             # Sort events by start time
            ).execute()
        )
        
        # Extract the events list from the API response
        events = events_result.get("items", [])
        
        # Create a new iCal calendar object
        cal = Calendar()
        
        # Process each event and add it to the iCal calendar
        for event in events:
            # Create a new iCal event
            cal_event = Event()
            
            # Extract start and end times (handle both datetime and date-only events)
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            # Add event properties to the iCal event
            cal_event.add('summary', event.get('summary', 'No Title'))  # Event title
            cal_event.add('dtstart', datetime.datetime.fromisoformat(start).astimezone(zoneinfo.ZoneInfo("UTC")))  # Start time
            cal_event.add('dtend', datetime.datetime.fromisoformat(end).astimezone(zoneinfo.ZoneInfo("UTC")))      # End time
            cal_event.add('description', event.get('description', ''))  # Event description
            cal_event.add('location', event.get('location', ''))        # Event location
            
            # Add the event to the calendar
            cal.add_component(cal_event)
        
        # Write the iCal data to a file
        with open('calendar.ics', 'wb') as f:
            f.write(cal.to_ical())
        
        print(f"Successfully created calendar.ics with {len(events)} events")
        
        # Open the iCal file with the default application
        try:
           subprocess.check_call(['xdg-open', 'calendar.ics'],
           stdout=subprocess.DEVNULL,
           stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
           print(f"Failed to open calendar.ics: {e}")
        except FileNotFoundError:
           print("xdg-open command not found. Please open calendar.ics manually.")
        
    except HttpError as error:
        print(f"An error occurred while accessing Google Calendar: {error}")

if __name__ == '__main__':
    main()
    