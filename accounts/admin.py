from django.contrib import admin

from accounts.models import User, LoginHistory


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    pass