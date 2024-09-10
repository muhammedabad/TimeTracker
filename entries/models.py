from django.db import models

from users.models import User


class Entry(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    date_created = models.DateField()

    class Meta:
        unique_together = ('user', 'date_created')
        verbose_name_plural = 'Entries'
        ordering = ['-date_created']

    def __str__(self):
        return f'{self.user} - {self.date_created}'


class JiraEntry(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.PROTECT)
    jira_issue_number = models.CharField(max_length=255)
    minutes_spent = models.IntegerField()
    description = models.TextField()
    jira_entry_id = models.CharField(max_length=20)
    last_synced_at = models.DateTimeField(null=True)

    @property
    def synced(self):
        return self.jira_entry_id is not None

    class Meta:
        unique_together = ('entry', 'jira_issue_number')
        verbose_name_plural = 'Jira Entries'


class RiseEntry(models.Model):
    ASSIGNMENT = 'assignment'
    PROJECT = 'project'

    entry = models.OneToOneField(Entry, on_delete=models.PROTECT)
    value = models.TextField(help_text="")
    hours_worked = models.DecimalField(max_digits=4, decimal_places=2, default=8.00)
    rise_entry_id = models.CharField(max_length=20)
    rise_assignment_id = models.CharField(max_length=20)
    rise_assignment_name = models.CharField(max_length=255)
    last_synced_at = models.DateTimeField(null=True)
    log_type = models.CharField(max_length=200, default=ASSIGNMENT)


    def delete(self, *args, **kwargs):
        # Custom code before deletion
        from entries.services import RiseAppService
        if self.rise_entry_id:
            rise_app_service = RiseAppService()
            rise_app_service.delete_entry(rise_entry=self)

        # Proceed with the actual deletion
        super().delete(*args, **kwargs)

    @property
    def synced(self):
        return self.rise_entry_id is not None

    def __str__(self):
        return f'{self.entry.user.username.title()} - {self.entry.date_created}'




