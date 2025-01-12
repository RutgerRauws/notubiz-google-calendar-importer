from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from notubiz import ApiClient, Configuration as NotubizConfig
from notubiz.api.clients import EventsClient, AssemblyClient, MeetingClient

from gcsa.google_calendar import GoogleCalendar

from scripts.config import Config
from scripts.add_to_gcal import NotubizGoogleCalendarImporter

config = Config.read_config()

date_start = datetime.combine(date.today(), datetime.min.time())
date_end = datetime.combine(
    date_start + relativedelta(weeks=config.weeks_ahead) + relativedelta(days=1), 
    datetime.min.time()
)

# Get a handle to Google Calendar
gc = GoogleCalendar(config.google_mail_address, credentials_path="./.credentials/credentials.json")

# First clear all existing events
existing_events = gc.get_events(
   time_min=date_start, 
   time_max=date_end,
   calendar_id=config.google_calendar_id
)

for event in existing_events:
    gc.delete_event(event=event, calendar_id=config.google_calendar_id)

#
# Retrieve events from Notubiz
#
configuration = NotubizConfig(config.organisation_id)
api_client = ApiClient(configuration)

event_client = EventsClient(api_client)
assembly_client = AssemblyClient(api_client)
meeting_client = MeetingClient(api_client)

notubiz_events = event_client.get(date_start, date_end)

# Get possible Notubiz assemblies/meetings and directly import them to Google Calendar
importer = NotubizGoogleCalendarImporter(gc, config.google_calendar_id)
for notubiz_event in notubiz_events:

    if notubiz_event.type == "assembly":
        try:
            assembly = assembly_client.get(notubiz_event.id)

            if len(assembly.meetings) == 0:
                importer.import_notubiz_event(assembly)
            else:
                for assembly_meeting in assembly.meetings:
                    meeting = meeting_client.get(assembly_meeting.id)
                    importer.import_notubiz_meeting(meeting, assembly_meeting)
        except: # In case we get a 'HTTP forbidden' (or something else)
            importer.import_notubiz_event(assembly) 
            
    else:
        importer.import_notubiz_event(notubiz_event)

print("Finished importing Notubiz events into Google Calendar")

