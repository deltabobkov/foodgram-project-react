from django.contrib import admin

from users.models import Subscribe, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
    )
    search_fields = (
        "first_name",
        "last_name",
    )
    list_filter = (
        "first_name",
        "last_name",
    )
    empty_value_display = "-пусто-"


class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "following",
        "user",
    )
    search_fields = (
        "following",
        "user",
    )
    list_filter = (
        "following",
        "user",
    )
    empty_value_display = "-пусто-"


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
