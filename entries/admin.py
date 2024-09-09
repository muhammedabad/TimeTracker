from django.contrib import admin
from django import forms
from django.utils import timezone

from entries.models import Entry, JiraEntry, RiseEntry
from users.models import User


class JiraEntryInline(admin.TabularInline):
    model = JiraEntry
    readonly_fields = ["synced", "jira_entry_id"]
    extra = 1  # Number of empty book forms to display by default


class RiseEntryInline(admin.TabularInline):
    model = RiseEntry
    readonly_fields = ["synced", "rise_entry_id"]
    extra = 1

    def has_add_permission(self, request, obj=None):
        if obj:  # If we're editing an existing Book instance
            return self.model.objects.filter(entry=obj).count() == 0  # Allow add only if no chapters exist
        return True  # Allow add on new Book instances


# Register your models here.
@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    inlines = [JiraEntryInline, RiseEntryInline]
    # readonly_fields = ["date_created"]

    def get_form(self, request, obj=None, **kwargs):
        # Get the form from the superclass
        form = super().get_form(request, obj, **kwargs)

        # When adding a new object (obj is None), default the 'user' field to the logged-in user
        if obj is None:
            # form.base_fields['user'].initial = request.user
            form.base_fields['user'].queryset = User.objects.filter(id=request.user.id)
            form.base_fields['user'].initial = request.user
            form.base_fields['date_created'].initial = timezone.now()

        return form
