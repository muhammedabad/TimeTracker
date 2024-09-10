import json

import requests
from django.conf import settings
from django.utils import timezone

from entries.models import RiseEntry
from users.models import User


class RiseApiClient:

    def __init__(self, user: User) -> None:
        self.user = user
        self.headers = {
            "Authorization": f"Token {self.user.rise_api_key}",
        }
        self.base_url = settings.RISE_API_URL
        self.start_date = timezone.now().date()
        self.end_date = timezone.now().date() + timezone.timedelta(days=7)

    def get_assignments(self) -> list or None:

        url = f"{self.base_url}/employees/dashboards/me/?from_date={self.start_date}&to_date={self.end_date}"
        response = requests.get(url, headers=self.headers)

        choices = [("", "----------")]
        if response.ok:
            for assignment in response.json().get("tables", {}).get("assignments", []):
                # assignment_start_date = assignment.get("start_date")
                # assignment_end_date = assignment.get("end_date")
                choices.append(
                    (assignment["id"], assignment["milestone"]["project"]["name"])
                )

            for project in response.json().get("tables", {}).get("global_projects", []):
                # project_start_date = assignment.get("start_date")
                # project_end_date = assignment.get("end_date")
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
            print(json.dumps(assignment))
            if str(assignment["id"]) == str(assignment_id):
                user_assignment = assignment

        if not user_assignment:
            # Check global projects
            for project in response.json().get("tables", {}).get("global_projects", []):
                # project_start_date = assignment.get("start_date")
                # project_end_date = assignment.get("end_date")
                print(project["id"], assignment_id)
                if str(project["id"]) == str(assignment_id):
                    user_assignment = project

        return user_assignment




    def create_entry(self, rise_entry: RiseEntry) -> None:
        pass

