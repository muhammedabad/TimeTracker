import requests
from django.conf import settings
from django.utils import timezone
from requests.auth import HTTPBasicAuth

from lib.utils import FernetCipher


class JiraApiClient:

    def __init__(self, user):
        self.base_url = user.jira_url

        # Decrypt API key
        api_key = FernetCipher().decrypt_value(user.jira_api_key)
        self.auth = HTTPBasicAuth(username=user.jira_email_address, password=api_key)

        self.headers = {
          "Accept": "application/json",
          "Content-Type": "application/json"
        }

    def create_entry(self, jira_entry):
        url = f"{self.base_url}/rest/api/3/issue/{jira_entry.jira_issue_number}/worklog"
        payload = {
          "comment": {
            "content": [
              {
                "content": [
                  {
                    "text": jira_entry.description,
                    "type": "text"
                  }
                ],
                "type": "paragraph"
              }
            ],
            "type": "doc",
            "version": 1
          },
          "started": timezone.now().strftime("%Y-%m-%dT%H:%M:%S.000%z"),
          "timeSpentSeconds": jira_entry.minutes_spent * 60,  # Convert to seconds
        }

        response = requests.post(
            url,
            json=payload,
            headers=self.headers,
            auth=self.auth
        )

        if response.ok:
            jira_entry.jira_entry_id = response.json().get('id')
            jira_entry.last_synced_at = timezone.now()
            jira_entry.save()

    def update_entry(self, jira_entry):
        url = f"{self.base_url}/rest/api/3/issue/{jira_entry.jira_issue_number}/worklog/{jira_entry.jira_entry_id}"
        payload = {
            "comment": {
                "content": [
                    {
                        "content": [
                            {
                                "text": jira_entry.description,
                                "type": "text"
                            }
                        ],
                        "type": "paragraph"
                    }
                ],
                "type": "doc",
                "version": 1
            },
            "started": timezone.now().strftime("%Y-%m-%dT%H:%M:%S.000%z"),
            "timeSpentSeconds": jira_entry.minutes_spent * 60,  # Convert to seconds
        }

        response = requests.put(
            url,
            json=payload,
            headers=self.headers,
            auth=self.auth
        )

        if response.ok:
            jira_entry.last_synced_at = timezone.now()
            jira_entry.save()

    def delete_entry(self, jira_entry):
        url = f"{self.base_url}/rest/api/3/issue/{jira_entry.jira_issue_number}/worklog/{jira_entry.jira_entry_id}"
        response = requests.delete(url=url, auth=self.auth)

