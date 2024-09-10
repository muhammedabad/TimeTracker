from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm as UnfoldAdminPasswordChangeForm
from unfold.forms import UserCreationForm, UserChangeForm
from unfold.widgets import UnfoldAdminPasswordInput

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
        if request.user.is_superuser:
            return (
                (None, {'fields': ('username', 'password')}),
                ('Personal info',
                 {'fields': ('email', 'first_name', 'last_name', 'rise_api_key', 'rise_user_id', 'jira_api_key')}),
                ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions', 'groups')}),
                ('Important dates', {'fields': ('last_login', 'date_joined')}),
            )
        else:
            return (
                (None, {'fields': ('username', 'password')}),
                ('Personal info',
                 {'fields': ('email', 'first_name', 'last_name', 'rise_api_key', 'rise_user_id', 'jira_api_key')}),
                # ('Important dates', {'fields': ('last_login', 'date_joined')}),
            )

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
