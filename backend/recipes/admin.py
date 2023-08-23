from django.contrib import admin
from django.db.models import Count

from .models import (
    Favorite, Ingredient, IngredientsInRecipe, Recipe, ShoppingCart, Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "color", "slug")
    search_fields = ("name",)
    list_editable = ("name",)
    list_filter = ("name", "color", "slug")
    empty_value_display = "-пусто-"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "measurement_unit")
    search_fields = ("name",)
    list_editable = ("name",)
    list_filter = ("name",)
    empty_value_display = "-пусто-"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "author", "text", "favorites")
    search_fields = (
        "author__username",
        "name",
        "author__email",
    )
    list_editable = ("name", "text")
    list_filter = ("name", "author", "tags")
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
        return obj.favorites.count()


@admin.register(IngredientsInRecipe)
class IngredientsInRecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "recipe", "ingredient", "amount")
    list_editable = ("recipe", "ingredient")
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
    search_fields = ("user__username", "user__email", "recipe__name")
    list_editable = ("user", "recipe")
    empty_value_display = "-пусто-"

    def get_queryset(self, request):
        queryset = (
            super().get_queryset(request).select_related("user", "recipe")
        )
        return queryset


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "recipe")
    search_fields = ("user__username", "user__email", "recipe__name")
    list_editable = ("user", "recipe")
    empty_value_display = "-пусто-"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("user", "recipe")
        return queryset
