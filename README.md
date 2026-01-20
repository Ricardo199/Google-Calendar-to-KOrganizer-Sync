# Google Calendar to KOrganizer Sync

A Python utility to sync Google Calendar events to KOrganizer by creating iCal files.

## Features

- Fetches upcoming events from Google Calendar
- Creates iCal (.ics) files compatible with KOrganizer
- Automatically imports events into KOrganizer on Linux systems
- Handles both datetime and date-only events

## Requirements

- Python 3.7+
- Google Calendar API credentials
- KOrganizer (for Linux import functionality)

## Installation

1. Clone this repository
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up Google Calendar API credentials (see Setup section)

## Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API
4. Create credentials (OAuth 2.0 client ID)
5. Download the credentials file and save it as `credentials.json` in the project directory

## Usage

Run the sync script:
```bash
python sync.py
```

The script will:
1. Authenticate with Google Calendar API
2. Fetch upcoming events
3. Create an iCal file (`google_calendar_events.ics`)
4. Import the events into KOrganizer

## Files

- `sync.py` - Main synchronization script
- `credentials.json` - Google API credentials (not included, you need to create this)
- `token.json` - OAuth token (generated automatically)
- `google_calendar_events.ics` - Generated iCal file

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.