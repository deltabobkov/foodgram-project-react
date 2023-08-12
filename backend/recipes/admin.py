from django.contrib import admin

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
    list_display = ("pk", "name", "units")
    search_fields = ("name",)
    list_editable = ("name",)
    list_filter = ("name",)
    empty_value_display = "-пусто-"

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "author", "description", "favorites")
    search_fields = (
        "author__username",
        "title",
        "author__email",
    )
    list_editable = ("title", "description")
    list_filter = ("title", "author", "tags")
    empty_value_display = "-пусто-"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("author").prefetch_related("tags","ingredients")
        return queryset

    def favorites(self, obj):
        return obj.favorites.count()

@admin.register(IngredientsInRecipe)
class IngredientsInRecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "recipe", "ingredient", "amount")
    list_editable = ("recipe", "ingredient")
    empty_value_display = "-пусто-"

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "recipe")
    search_fields = ("user__username", "user__email", "recipe__name")
    list_editable = ("user", "recipe")
    empty_value_display = "-пусто-"

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "recipe")
    search_fields = ("user__username", "user__email", "recipe__name")
    list_editable = ("user", "recipe")
    empty_value_display = "-пусто-"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("user")
        return queryset
    