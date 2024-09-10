from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    rise_api_key = models.CharField(max_length=255, null=True, blank=True, help_text="RiseApp API Key")
    rise_user_id = models.IntegerField(help_text="RiseApp user ID", blank=True, null=True)
    jira_api_key = models.CharField(max_length=255, null=True, blank=True, help_text="Jira API Key")






