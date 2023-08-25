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
        "email",
    )
    empty_value_display = "-пусто-"


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "user",
    )
    search_fields = (
        "author",
        "user",
    )
    list_filter = (
        "author",
        "user",
    )
    empty_value_display = "-пусто-"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("user", "author")
        return queryset
