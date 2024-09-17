from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    rise_api_key = models.TextField(null=True, blank=True, help_text="RiseApp API Key")
    rise_user_id = models.IntegerField(help_text="RiseApp User ID", blank=True, null=True)
    jira_email_address = models.EmailField(help_text="Jira Email Address", blank=True, null=True)
    jira_api_key = models.TextField(null=True, blank=True, help_text="Jira API Key")
    jira_url = models.URLField(max_length=255, null=True, blank=True, help_text="e.g. https://testing.atlassian.net")

    def __str__(self):
        return self.get_full_name()

    class Meta:
        verbose_name = "User Account"






