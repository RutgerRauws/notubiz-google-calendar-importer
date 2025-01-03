from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from notubiz import ApiClient, Configuration as NotubizConfig
from notubiz.api.clients import EventsClient

from gcsa.google_calendar import GoogleCalendar
from gcsa.event import Event as GoogleEvent

from scripts.config import Config

config = Config.read_config()

#
# Retrieve events from Notubiz
#
configuration = NotubizConfig(config.organisation_id)
api_client = ApiClient(configuration)

event_client = EventsClient(api_client)

date_start = datetime.combine(date.today(), datetime.min.time())
date_end = datetime.combine(
    date_start + relativedelta(weeks=config.weeks_ahead) + relativedelta(days=1), 
    datetime.min.time()
)

notubiz_events = event_client.get(date_start, date_end)

#
# Import the calendar into Google Calendar
#
gc = GoogleCalendar(config.google_mail_address, credentials_path="./.credentials/credentials.json")

# First clear all existing events
existing_events = gc.get_events(
    time_min=date_start, 
    time_max=date_end,
    calendar_id=config.google_calendar_id
)

for event in existing_events:
    gc.delete_event(event=event, calendar_id=config.google_calendar_id)

# Add Notubiz events in Google Calendar
for notubiz_event in notubiz_events:
    
    if len(notubiz_event.plannings) == 0: continue
    if notubiz_event.canceled: continue

    event = GoogleEvent(
        summary      = notubiz_event.title,
        start        = notubiz_event.plannings[0].start_date,
        end          = notubiz_event.plannings[0].end_date,
        location     = notubiz_event.location,
        #description = TODO
        minutes_before_popup_reminder = 15
    )

    gc.add_event(event=event, calendar_id=config.google_calendar_id)

print("Finished importing Notubiz events into Google Calendar")