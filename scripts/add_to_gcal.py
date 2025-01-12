from notubiz.api.dataclasses import Event as NotubizEvent
from notubiz.api.dataclasses import Meeting as NotubizMeeting
from notubiz.api.dataclasses.assembly import AssemblyMeeting as NotubizAssemblyMeeting

from gcsa.event import Event as GoogleEvent
from gcsa.google_calendar import GoogleCalendar

class NotubizGoogleCalendarImporter:
    def __init__(self, gc: GoogleCalendar, gc_calendar_id: str) -> None:
        self.gc = gc
        self.gc_calendar_id = gc_calendar_id

    def import_notubiz_event(self, nb_event: NotubizEvent) -> None:
        if len(nb_event.plannings) == 0: return
        if nb_event.canceled: return

        event = GoogleEvent(
            summary      = nb_event.title,
            start        = nb_event.plannings[0].start_date,
            end          = nb_event.plannings[0].end_date,
            location     = nb_event.location,
            minutes_before_popup_reminder = 15
        )
        
        self.gc.add_event(event=event, calendar_id=self.gc_calendar_id)
    
    def import_notubiz_meeting(self, nb_meeting: NotubizMeeting, nb_assembly_meeting: NotubizAssemblyMeeting) -> None:
        if nb_meeting.canceled or nb_meeting.inactive:
            return

        if len(nb_meeting.agenda_items) == 0:
            gc_event = GoogleEvent(
                summary     = nb_meeting.title,
                start       = nb_assembly_meeting.plannings[0].start_date,
                end         = nb_assembly_meeting.plannings[0].end_date,
                location    = nb_meeting.location,
                description = nb_meeting.url,
                minutes_before_popup_reminder = 15
            )

            self.gc.add_event(event=gc_event, calendar_id=self.gc_calendar_id)
            return
        
        else:
            for nb_agenda_item in nb_meeting.agenda_items:
                if nb_agenda_item.is_heading: continue

                gc_event = GoogleEvent(
                    summary     = nb_agenda_item.title,
                    start       = nb_agenda_item.start_date,
                    end         = nb_agenda_item.end_date,
                    location    = nb_meeting.location,
                    description = "{} \n\n {}".format(nb_agenda_item.description, nb_meeting.url),
                    minutes_before_popup_reminder = 15
                )

                self.gc.add_event(event=gc_event, calendar_id=self.gc_calendar_id)