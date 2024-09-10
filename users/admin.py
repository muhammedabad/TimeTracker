from django.contrib import admin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from users.models import User

# Register your models here.
admin.site.register(User, ModelAdmin)
admin.site.unregister(Group)
admin.site.register(Group, ModelAdmin)
