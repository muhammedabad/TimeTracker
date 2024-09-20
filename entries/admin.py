from typing import List, Tuple, Dict, Any

from django import forms
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.core.exceptions import ValidationError
from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils import timezone
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline
from unfold.contrib.filters.admin import RangeDateFilter
from unfold.widgets import UnfoldAdminSelectWidget, UnfoldAdminTextInputWidget

from api_clients.rise import RiseApiClient
from entries.models import Entry, JiraEntry, RiseEntry
from entries.services import RiseAppService, JiraService
from lib.utils import format_date
from users.models import User


class CustomUnfoldSelectWidget(UnfoldAdminSelectWidget):
    pass


class JiraEntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(JiraEntryForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields["jira_issue_number"] = forms.CharField(
                widget=UnfoldAdminTextInputWidget(attrs={'readonly': 'readonly'}))
            self.fields["last_synced_at"] = forms.DateTimeField(
                widget=UnfoldAdminTextInputWidget(attrs={'readonly': 'readonly'}), required=False)
        else:
            self.fields["last_synced_at"] = forms.DateTimeField(
                widget=UnfoldAdminTextInputWidget(attrs={"disabled": "disabled"}), required=False, initial="-")

    def clean(self):
        cleaned_data = super(JiraEntryForm, self).clean()
        if not all([self.user.jira_api_key, self.user.jira_email_address, self.user.jira_url]):
            self.add_error('description', "Please check your JIRA config in your user settings.")

        return cleaned_data

    def save(self, commit=True):
        # Check if the specific field has changed
        instance = super(JiraEntryForm, self).save(commit=commit)

        if self.has_changed() and 'description' in self.changed_data or 'minutes_spent' in self.changed_data:
            jira_client = JiraService()
            if instance.jira_entry_id:
                # Update the entry
                jira_client.update_entry(jira_entry=instance)
            else:
                # Create the entry
                jira_client.create_entry(jira_entry=instance)

        return instance

    class Meta:
        model = JiraEntry
        exclude = ("jira_entry_id",)


class JiraEntryInline(TabularInline):
    model = JiraEntry
    form = JiraEntryForm
    can_delete = False
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        """
        Override get_formset to pass user object into the formset's form initialization.
        """
        formset_class = super().get_formset(request, obj, **kwargs)

        class CustomFormset(formset_class):
            def __init__(self, *args, **kwargs):
                # Inject the user's email into each form
                self.user = request.user
                super(CustomFormset, self).__init__(*args, **kwargs)
                self.extra = 0  # Set to 0 to avoid extra empty forms

            def _construct_form(self, i, **kwargs):
                # Pass the user_email when constructing each form
                kwargs['user'] = self.user
                return super()._construct_form(i, **kwargs)

        return CustomFormset


class RiseInlineForm(forms.ModelForm):
    rise_assignment_id = forms.ChoiceField(choices=[], label="RiseApp Project")
    rise_assignment_name = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = RiseEntry  # Your Rise model
        exclude = ("rise_entry_id", "log_type",)

    def clean(self):
        cleaned_data = super(RiseInlineForm, self).clean()
        if not self.user.rise_api_key:
            self.add_error('value', "You need to add your Rise API key in your user settings.")

        if cleaned_data.get("rise_assignment_id"):
            # Get the entry date and rise assignment
            entry_date = cleaned_data.get("entry").date_created
            rise_assignment = self.get_single_assignment(user=cleaned_data.get("entry").user, assignment_id=cleaned_data.get("rise_assignment_id"))

            # Get assignment start and end dates
            assignment_start_date = timezone.datetime.strptime(rise_assignment["start_date"],"%Y-%m-%d").date()
            assignment_end_date = timezone.datetime.strptime(rise_assignment["end_date"],"%Y-%m-%d").date()

            if entry_date < assignment_start_date or entry_date > assignment_end_date:
                self.add_error('rise_assignment_id', 'Please select a project within the correct date range')

        return cleaned_data

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        self.user = user
        super(RiseInlineForm, self).__init__(*args, **kwargs)

        # Customize fields
        self.fields["rise_assignment_id"].widget = UnfoldAdminSelectWidget()
        self.fields['rise_entry_id'] = forms.CharField(widget=forms.HiddenInput(), required=False)

        # Set assignments to the current value in edit mode
        if self.instance.pk:

            # Limit the assignment dropdown options to the current value
            assignment_details = self.get_single_assignment(user=self.instance.entry.user, assignment_id=self.instance.rise_assignment_id)
            self.fields["rise_assignment_id"].choices = [
                (self.instance.rise_assignment_id, f'{self.instance.rise_assignment_name} ({format_date(assignment_details["start_date"])} - {format_date(assignment_details["end_date"])})')
            ]

            self.fields['last_synced_at'] = forms.DateTimeField(
                widget=UnfoldAdminTextInputWidget(attrs={"readonly": "readonly"}), required=False)

        else:
            if user and self.user.rise_api_key:
                # Get user assignments
                user_assignments = self.get_assignments()

                # Set assignment choices
                self.fields["rise_assignment_id"].choices = user_assignments

                # Default sync date to an empty value as this is a new record
                self.fields['last_synced_at'] = forms.DateTimeField(
                    widget=UnfoldAdminTextInputWidget(attrs={"disabled": "disabled"}), required=False, initial="-")
            else:
                self.fields["value"] = forms.CharField(widget=UnfoldAdminTextInputWidget(
                    attrs={"disabled": "disabled", "value": "Invalid Rise API key"}
                ))
                self.fields['last_synced_at'] = forms.DateTimeField(
                    widget=UnfoldAdminTextInputWidget(attrs={"disabled": "disabled"}), required=False, initial="-")

    def get_assignments(self):
        # Get assignments for this user
        rise_client = RiseApiClient(user=self.user)
        return rise_client.get_assignments()

    @staticmethod
    def get_single_assignment(user: User, assignment_id: int):
        # Get the details for a single assignment
        rise_api_call = RiseApiClient(user=user)
        return rise_api_call.get_single_assignment(assignment_id=assignment_id)

    def save(self, commit=True):

        instance = super(RiseInlineForm, self).save(commit=False)
        assignment_details = self.get_single_assignment(user=self.user, assignment_id=instance.rise_assignment_id)

        if "is_global" in assignment_details:
            # This is a global project
            instance.rise_assignment_name = assignment_details["name"]
            instance.log_type = RiseEntry.PROJECT
        else:
            instance.rise_assignment_name = assignment_details["milestone"]["project"]["name"]
            instance.log_type = RiseEntry.ASSIGNMENT

        # Set the ID of the assignment
        instance.rise_assignment_id = assignment_details["id"]

        # Save the form instance
        if commit:
            instance.save()

            # Check if the specific field has changed
            if self.has_changed() and 'value' in self.changed_data or 'hours_worked' in self.changed_data:
                rise_client = RiseAppService()
                if instance.rise_entry_id:
                    # Update the entry
                    rise_client.update_entry(rise_entry=instance)
                else:
                    # Create the entry
                    rise_client.create_entry(rise_entry=instance)

                return instance


class RiseInline(TabularInline):
    model = RiseEntry
    form = RiseInlineForm

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(RiseInline, self).get_readonly_fields(request, obj)
        if obj:  # Check if in edit mode
            return self.readonly_fields + ("rise_entry_id",)
        else:
            return self.readonly_fields

    def get_formset(self, request, obj=None, **kwargs):
        """
        Override get_formset to pass user object into the formset's form initialization.
        """
        formset_class = super().get_formset(request, obj, **kwargs)

        class CustomFormset(formset_class):
            def __init__(self, *args, **kwargs):
                # Inject the user's email into each form
                self.user = request.user
                super(CustomFormset, self).__init__(*args, **kwargs)
                self.extra = 1  # Set to 0 to avoid extra empty forms

            def _construct_form(self, i, **kwargs):
                # Pass the user_email when constructing each form
                kwargs['user'] = self.user
                return super()._construct_form(i, **kwargs)

        return CustomFormset


class CustomRangeDateFilter(RangeDateFilter):
    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet | None:
        filters = {}

        value_from = self.used_parameters.get(self.parameter_name + "_from", None)
        if value_from not in EMPTY_VALUES:
            filters.update(
                {
                    self.parameter_name
                    + "__gte": self.used_parameters.get(
                        self.parameter_name + "_from", None
                    ),
                }
            )

        value_to = self.used_parameters.get(self.parameter_name + "_to", None)
        if value_to not in EMPTY_VALUES:
            filters.update(
                {
                    self.parameter_name
                    + "__lte": self.used_parameters.get(
                        self.parameter_name + "_to", None
                    ),
                }
            )

        try:
            return queryset.filter(**filters)
        except (ValueError, ValidationError):
            return None

    def expected_parameters(self) -> List[str]:
        return [
            f"{self.parameter_name}_from",
            f"{self.parameter_name}_to",
        ]

    def choices(self, changelist: ChangeList) -> Tuple[Dict[str, Any], ...]:
        return (
            {
                "request": self.request,
                "parameter_name": self.parameter_name,
                "form": self.form_class(
                    name=self.parameter_name,
                    data={
                        self.parameter_name
                        + "_from": self.used_parameters.get(
                            self.parameter_name + "_from", None
                        ),
                        self.parameter_name
                        + "_to": self.used_parameters.get(
                            self.parameter_name + "_to", None
                        ),
                    },
                ),
            },
        )


@admin.register(Entry)
class EntryAdmin(ModelAdmin):
    inlines = [JiraEntryInline, RiseInline]
    list_display = ["user", "date_created", "total_jira_hours", "total_rise_hours"]
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = (
        ("date_created", CustomRangeDateFilter),
    )

    def get_queryset(self, request):
        """
        Return the queryset for the admin list view based on user permissions.
        """
        qs = super().get_queryset(request)

        # Check if the user is a superuser
        if not request.user.is_superuser:
            # Filter the queryset to include only entries related to the logged-in user
            qs = qs.filter(user=request.user)

        return qs

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


# admin.site.register(RiseEntry, ModelAdmin)
# admin.site.register(JiraEntry, ModelAdmin)
