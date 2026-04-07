from datetime import timedelta

from notubiz.api.dataclasses import Event as NotubizEvent
from notubiz.api.dataclasses import Meeting as NotubizMeeting
from notubiz.api.dataclasses.assembly import AssemblyMeeting as NotubizAssemblyMeeting

from scripts.google_calendar_client import GoogleCalendarClient

class NotubizGoogleCalendarImporter:
    def __init__(self, gc: GoogleCalendarClient, gc_calendar_id: str) -> None:
        self.gc = gc
        self.gc_calendar_id = gc_calendar_id

    def import_notubiz_event(self, nb_event: NotubizEvent) -> None:
        if len(nb_event.plannings) == 0: return
        if nb_event.canceled: return

        event = {
            "summary": nb_event.title,
            **self.convert_agenda_item_to_date(nb_event.plannings[0]),
            "location": nb_event.location,
            "reminders": {
                "useDefault": False,
                "overrides": [{"method": "popup", "minutes": 15}],
            },
        }
        
        self.gc.add_event(event=event, calendar_id=self.gc_calendar_id)
    
    def import_notubiz_meeting(self, nb_meeting: NotubizMeeting, nb_assembly_meeting: NotubizAssemblyMeeting) -> None:
        if nb_meeting.canceled or nb_meeting.inactive:
            return

        if len(nb_meeting.agenda_items) == 0:
            gc_event = {
                "summary": nb_meeting.title,
                **self.convert_agenda_item_to_date(nb_assembly_meeting.plannings[0]),
                "location": nb_meeting.location,
                "description": nb_meeting.url,
                "reminders": {
                    "useDefault": False,
                    "overrides": [{"method": "popup", "minutes": 15}],
                },
            }

            self.gc.add_event(event=gc_event, calendar_id=self.gc_calendar_id)
            return
        
        else:
            for nb_agenda_item in nb_meeting.agenda_items:
                if nb_agenda_item.is_heading: continue

                gc_event = {
                    "summary": nb_agenda_item.title,
                    **self.convert_agenda_item_to_date(nb_agenda_item),
                    "location": nb_meeting.location,
                    "description": "{} \n\n {}".format(nb_agenda_item.description, nb_meeting.url),
                    "reminders": {
                        "useDefault": False,
                        "overrides": [{"method": "popup", "minutes": 15}],
                    },
                }

                self.gc.add_event(event=gc_event, calendar_id=self.gc_calendar_id)
    
    @staticmethod
    def convert_agenda_item_to_date(nb_agenda_item) -> dict:
        start_date = nb_agenda_item.start_date
        end_date = nb_agenda_item.end_date

        if start_date is None:
            raise ValueError("Agenda item does not have a start date, cannot be imported to Google Calendar")

        if end_date is None:
            end_date = start_date + timedelta(minutes=60)

        return {
            "start": {
                "dateTime": start_date.isoformat(),
                "timeZone": "Europe/Amsterdam"
            },
            "end": {
                "dateTime": end_date.isoformat(),
                "timeZone": "Europe/Amsterdam"
            }
        }