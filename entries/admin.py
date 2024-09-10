from django import forms
from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.utils import timezone

from api_clients.rise import RiseApiClient
from entries.models import Entry, JiraEntry, RiseEntry
from users.models import User


class JiraEntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(JiraEntryForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields["jira_issue_number"] = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
            self.fields["last_synced_at"] = forms.DateField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
        else:
            self.fields["last_synced_at"] = forms.DateField(widget=forms.TextInput(attrs={"disabled": "disabled"}), required=False, initial="-")

    class Meta:
        model = JiraEntry
        exclude = ("jira_entry_id",)


class JiraEntryInline(admin.TabularInline):
    model = JiraEntry
    form = JiraEntryForm


class RiseInlineForm(forms.ModelForm):
    rise_assignment_id = forms.ChoiceField(choices=[], label="RiseApp Project")
    rise_assignment_name = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = RiseEntry  # Your Rise model
        # fields = '__all__'
        exclude = ("rise_entry_name",)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        self.user = user
        super(RiseInlineForm, self).__init__(*args, **kwargs)

        self.fields['rise_entry_id'] = forms.CharField(widget=forms.HiddenInput(), required=False)

        # Fetch data from the 3rd party API using the user's email
        if self.instance.pk:
            # self.fields['rise_assignment_id'].initial = self.instance.rise_assignment_id
            self.fields["rise_assignment_name"] = forms.ChoiceField(
                widget=forms.Select(attrs={"readonly": "readonly"}),
                choices=[(self.instance.rise_assignment_id, self.instance.rise_assignment_name)],
                label="RiseApp Project"
            )
            self.fields['rise_assignment_id'] = forms.CharField(widget=forms.HiddenInput())
            self.fields["last_synced_at"] = forms.DateField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

        else:
            if user:
                api_choices = self.get_assignments()
                self.fields['rise_assignment_id'].choices = api_choices
                self.fields["last_synced_at"] = forms.DateField(widget=forms.TextInput(attrs={"disabled": "disabled"}),
                                                                required=False, initial="-")


    def get_assignments(self):
        # Get assignments for this user
        rise_api_call = RiseApiClient(user=self.user)
        return rise_api_call.get_assignments()

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
        else:
            instance.rise_assignment_name = assignment_details["milestone"]["project"]["name"]

        instance.rise_assignment_id = assignment_details["id"]

        if commit:
            instance.save()

        return instance


class RiseInline(admin.TabularInline):
    model = RiseEntry
    form = RiseInlineForm

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(RiseInline, self).get_readonly_fields(request, obj)
        if obj:  # Check if in edit mode
            return self.readonly_fields + ("rise_entry_id", )
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

            def _construct_form(self, i, **kwargs):
                # Pass the user_email when constructing each form
                kwargs['user'] = self.user
                return super()._construct_form(i, **kwargs)

        return CustomFormset


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    inlines = [JiraEntryInline, RiseInline]

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


admin.site.register(RiseEntry)
admin.site.register(JiraEntry)