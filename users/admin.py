from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from unfold.forms import UserCreationForm
from unfold.widgets import UnfoldAdminPasswordInput

from users.models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = UnfoldAdminPasswordInput()
        self.fields['password2'].widget = UnfoldAdminPasswordInput()


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget = UnfoldAdminPasswordInput()


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ['username', 'email', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'email']
    ordering = ['username']


admin.site.unregister(Group)
@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass