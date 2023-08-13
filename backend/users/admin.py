from django.contrib import admin

from users.models import Subscribe, User


@admin.register(User)
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


@admin.register(Subscribe)
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

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("user")
        return queryset
