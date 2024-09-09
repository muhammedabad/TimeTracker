from django.db import models

from users.models import User


class Entry(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    date_created = models.DateTimeField()

    class Meta:
        unique_together = ('user', 'date_created')
        verbose_name_plural = 'Entries'
        ordering = ['-date_created']

    def __str__(self):
        return f'{self.user} - {self.date_created.date()}'


class JiraEntry(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.PROTECT)
    jira_issue_number = models.CharField(max_length=255)
    minutes_spent = models.IntegerField()
    description = models.TextField()
    jira_entry_id = models.CharField(max_length=20)
    synced = models.BooleanField(default=False)

    class Meta:
        unique_together = ('entry', 'jira_issue_number')
        verbose_name_plural = 'Jira Entries'


class RiseEntry(models.Model):
    entry = models.OneToOneField(Entry, on_delete=models.PROTECT)
    value = models.TextField(help_text="")
    rise_entry_id = models.CharField(max_length=20)
    synced = models.BooleanField(default=False)




