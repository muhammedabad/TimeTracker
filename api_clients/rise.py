import json

import requests
from django.conf import settings
from django.utils import timezone

from entries.models import RiseEntry
from lib.utils import FernetCipher
from users.models import User


class RiseApiClient:

    def __init__(self, user: User) -> None:
        self.user = user

        # Set auth by decrypting api key
        api_key = FernetCipher().decrypt_value(self.user.rise_api_key)
        self.headers = {
            "Authorization": f"Token {api_key}",
        }

        self.base_url = settings.RISE_API_URL
        self.start_date = timezone.now().date()
        self.end_date = timezone.now().date() + timezone.timedelta(days=7)

    def get_assignments(self) -> list or None:

        url = f"{self.base_url}/employees/dashboards/me/?from_date={self.start_date}&to_date={self.end_date}"
        response = requests.get(url, headers=self.headers)

        choices = [("", "Select A Project")]
        if response.ok:
            for assignment in response.json().get("tables", {}).get("assignments", []):
                choices.append(
                    (assignment["id"], assignment["milestone"]["project"]["name"])
                )

            for project in response.json().get("tables", {}).get("global_projects", []):
                choices.append(
                    (project['id'], project["name"])
                )

            return choices

        return None

    def get_single_assignment(self, assignment_id: int) -> dict:
        url = f"{self.base_url}/employees/dashboards/me/?from_date={self.start_date}&to_date={self.end_date}"
        response = requests.get(url, headers=self.headers)
        user_assignment = None

        for assignment in response.json().get("tables", {}).get("assignments", []):
            if str(assignment["id"]) == str(assignment_id):
                user_assignment = assignment

        if not user_assignment:
            # Check global projects
            for project in response.json().get("tables", {}).get("global_projects", []):
                if str(project["id"]) == str(assignment_id):
                    user_assignment = project

        return user_assignment

    def create_entry(self, rise_entry: RiseEntry) -> None:
        # Define base request info
        url = f"{self.base_url}/employees/{rise_entry.entry.user.rise_user_id}/actions/log/"
        data = {
            "day": rise_entry.entry.date_created.isoformat(),
            "hours": str(rise_entry.hours_worked),
            "description": rise_entry.value
        }

        if rise_entry.log_type == RiseEntry.ASSIGNMENT:
            data["assignment"] = rise_entry.rise_assignment_id
        else:
            data["project"] = rise_entry.rise_assignment_id

        # Make the request
        result = requests.post(url, headers=self.headers, json=data)

        # Update local entry
        if result.ok:
            rise_entry.rise_entry_id = result.json()["id"]
            rise_entry.last_synced_at = timezone.now()
            rise_entry.save()

    def update_entry(self, rise_entry: RiseEntry) -> None:
        # Define base request info
        url = f"{self.base_url}/timesheets/{rise_entry.rise_entry_id}/actions/edit_log/"
        data = {
            "hours_recorded": str(rise_entry.hours_worked),
            "description": rise_entry.value
        }

        # Make the request
        result = requests.post(url, headers=self.headers, json=data)

        # Update local rise entry
        if result.ok:
            rise_entry.last_synced_at = timezone.now()
            rise_entry.save()

    def delete_entry(self, rise_entry: RiseEntry) -> None:
        url = f"{self.base_url}/timesheets/{rise_entry.rise_entry_id}/actions/delete/"
        requests.post(url, headers=self.headers, json={})
