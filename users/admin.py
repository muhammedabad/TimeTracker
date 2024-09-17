from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django import forms
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm as UnfoldAdminPasswordChangeForm
from unfold.forms import UserCreationForm, UserChangeForm
from unfold.widgets import UnfoldAdminPasswordInput
from unfold.widgets import UnfoldAdminTextInputWidget


from lib.utils import FernetCipher
from users.models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("password1", "password2", "rise_api_key")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = UnfoldAdminPasswordInput()
        self.fields['password2'].widget = UnfoldAdminPasswordInput()


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('rise_api_key', 'rise_user_id', 'jira_api_key')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Define help text for encrypted fields
        encryption_help_text = "Note: Values in this field are encrypted when saved"

        self.fields['rise_api_key'] = forms.CharField(
            widget=UnfoldAdminTextInputWidget(attrs={'autocomplete': 'off'}),
            required=False,
            help_text=encryption_help_text
        )

        self.fields['jira_api_key'] = forms.CharField(
            widget=UnfoldAdminTextInputWidget(attrs={'autocomplete': 'off'}),
            required=False,
            help_text=encryption_help_text
        )

    def save(self, commit=False):
        instance = super(CustomUserChangeForm, self).save(commit=commit)

        # Strip unwanted spaces
        instance.rise_api_key = self.cleaned_data['rise_api_key'].strip()
        instance.jira_api_key = self.cleaned_data['jira_api_key'].strip()

        # Instantiate cipher to encrypt sensitive data
        cipher = FernetCipher()

        if "rise_api_key" in self.changed_data:
            if instance.rise_api_key != "":
                instance.rise_api_key = cipher.encrypt_value(value=instance.rise_api_key)

        if "jira_api_key" in self.changed_data:
            if instance.jira_api_key != "":
                instance.jira_api_key = cipher.encrypt_value(value=instance.jira_api_key)

        # Update instance
        instance.save(update_fields=['rise_api_key', 'jira_api_key'])

        return instance


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    change_password_form = UnfoldAdminPasswordChangeForm
    model = User
    list_display = ['username', 'email', 'is_staff', 'is_active', ]
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'email']
    ordering = ['username']

    def get_fieldsets(self, request, obj=None):
        """
        Return the fieldsets to use in the admin form.
        """
        if obj:
            if request.user.is_superuser:
                return (
                    (None, {'fields': ('username', 'password')}),
                    ('Personal info', {'fields': ('email', 'first_name', 'last_name',)}),
                    ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions', 'groups')}),
                    ('Important dates', {'fields': ('last_login', 'date_joined')}),
                    ('Integration Settings', {'fields': ('rise_api_key', 'rise_user_id', 'jira_url', 'jira_email_address', 'jira_api_key',)}),
                )
            else:
                return (
                    (None, {'fields': ('username', 'password')}),
                    ('Personal info', {'fields': ('email', 'first_name', 'last_name',)}),
                    ('Integration Settings', {'fields': ('rise_api_key', 'rise_user_id', 'jira_url', 'jira_email_address', 'jira_api_key',)}),

                )
        return super().get_fieldsets(request, obj)

    def get_queryset(self, request):
        """
        Return the queryset for the admin list view based on user permissions.
        """
        qs = super().get_queryset(request)

        # Check if the user is a superuser
        if not request.user.is_superuser:
            # Filter the queryset to include only entries related to the logged-in user
            qs = qs.filter(id=request.user.id)

        return qs


admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
