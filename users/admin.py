from django.contrib import admin

# Register your models here.

from users.models import CustomUser
from django.contrib.auth.admin import UserAdmin


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ["id", "email", "is_active"]
    ordering = ["email"]
    fieldsets = (
        (None, {"fields": ("email", "password", "is_active")}),
        ("Personal info", {"fields": ("last_login", "is_superuser")}),
    )
