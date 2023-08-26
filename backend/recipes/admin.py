from django.contrib import admin
from django.db.models import Count

from .models import (
    Favorite, Ingredient, IngredientsInRecipe, Recipe, ShoppingCart, Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "color", "slug")
    list_display_links = ("name",)
    search_fields = ("name",)
    list_filter = ("color",)
    empty_value_display = "-пусто-"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "measurement_unit")
    list_display_links = ("name",)
    search_fields = ("name",)
    empty_value_display = "-пусто-"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "author", "text", "favorites")
    list_display_links = ("name",)
    search_fields = (
        "author__username",
        "name",
        "author__email",
    )
    list_filter = ("author", "tags")
    empty_value_display = "-пусто-"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = (
            queryset.select_related("author")
            .prefetch_related("tags", "ingredients")
            .annotate(favorited=Count("favorites"))
        )
        return queryset

    def favorites(self, obj):
        return obj.favorited


@admin.register(IngredientsInRecipe)
class IngredientsInRecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "recipe", "ingredient", "amount")
    list_display_links = ("recipe", "ingredient")
    empty_value_display = "-пусто-"

    def get_queryset(self, request):
        queryset = (
            super()
            .get_queryset(request)
            .select_related("recipe")
            .prefetch_related("ingredient")
        )
        return queryset


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "recipe")
    list_display_links = ("user", "recipe")
    search_fields = ("user__username", "user__email", "recipe__name")
    empty_value_display = "-пусто-"

    def get_queryset(self, request):
        queryset = (
            super().get_queryset(request).select_related("user", "recipe")
        )
        return queryset


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "recipe")
    list_display_links = ("user", "recipe")
    search_fields = ("user__username", "user__email", "recipe__name")
    empty_value_display = "-пусто-"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("user", "recipe")
        return queryset
