from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GoogleCalendarClient:
    SCOPES = ["https://www.googleapis.com/auth/calendar"]

    def __init__(self, credentials_path: str, token_path: str = "./.credentials/token.json") -> None:
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = self._build_service()

    def _build_service(self):
        creds = None

        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)

            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, "w") as token:
                token.write(creds.to_json())

        return build("calendar", "v3", credentials=creds)

    @staticmethod
    def _to_rfc3339(value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()

    def get_events(self, time_min: datetime, time_max: datetime, calendar_id: str) -> list[dict[str, Any]]:
        result = (
            self.service.events()
            .list(
                calendarId=calendar_id,
                timeMin=self._to_rfc3339(time_min),
                timeMax=self._to_rfc3339(time_max),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        return result.get("items", [])

    def delete_event(self, event: dict[str, Any], calendar_id: str) -> None:
        event_id = event.get("id")
        if not event_id:
            return

        self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

    def add_event(self, event: dict[str, Any], calendar_id: str) -> None:
        self.service.events().insert(calendarId=calendar_id, body=event).execute()
