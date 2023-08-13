from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr="startswith")

    class Meta:
        model = Ingredient
        fields = ("name",)


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )

    is_favorited = filters.BooleanFilter(method="is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(method="is_in_shopping_cart")

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "author",
        )

    def is_favorited(self, queryset, title, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorite_recipes__user=user)
        return queryset

    def is_in_shopping_cart(self, queryset, title, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shopping_cart__user=user)
        return queryset
