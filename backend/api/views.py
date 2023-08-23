from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from recipes.models import (
    Favorite, Ingredient, IngredientsInRecipe, Recipe, ShoppingCart, Tag,
)
from users.models import Subscribe, User

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsOwnerOrAdminOrReadOnly
from .serializers import (
    CreateRecipeSerializer, GetRecipeSerializer, IngredientSerializer,
    RecipeSerializer, SubscriptionsSerializer, TagSerializer, UserSerializer,
)


class IngredientViewSet(ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsOwnerOrAdminOrReadOnly,)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.select_related("author").prefetch_related(
        "tags", "ingredients"
    )
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return GetRecipeSerializer
        return CreateRecipeSerializer

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        if request.method == "POST":
            recipe = get_object_or_404(Recipe, id=pk)
            obj, created = Favorite.objects.get_or_create(
                user=request.user, recipe=recipe
            )
            if created:
                serializer = RecipeSerializer(recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                {"Ошибка": "Рецепт уже есть в избранном"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj = Favorite.objects.filter(
            user=request.user, recipe__id=pk
        ).delete()

        if obj[0] > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"Ошибка": "Рецепта нет в избранном"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        if request.method == "POST":
            recipe = get_object_or_404(Recipe, id=pk)
            obj, created = ShoppingCart.objects.get_or_create(
                user=request.user, recipe=recipe
            )
            if created:
                serializer = RecipeSerializer(recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                {"Ошибка": "Рецепт уже есть в списке покупок"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        obj = ShoppingCart.objects.filter(
            user=request.user, recipe__id=pk
        ).delete()

        if obj[0] > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"Ошибка": "Рецепта нет в списке покупок"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = user.shopping_cart.all()
        if not shopping_cart:
            return Response(
                "Список покупок пуст.", status=status.HTTP_400_BAD_REQUEST
            )
        ingredients = (
            IngredientsInRecipe.objects.filter(
                recipe__shopping_cart__user=user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(amount=Sum("amount"))
        )

        response = HttpResponse(
            self.generate_shopping_file(ingredients, user),
            content_type="text/plain",
        )
        response["Content-Disposition"] = "attachment; filename='shoplist.txt'"
        return response

    def generate_shopping_file(self, ingredients, user):
        content = f"Список покупок {user.get_full_name()}:\n\n"
        for ingredient in ingredients:
            name = ingredient.get("ingredient__name")
            units = ingredient.get("ingredient__measurement_unit")
            amount = ingredient.get("amount")
            content += f"{name} ({units}) - {amount}\n"
        return content


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user).annotate(
            recipes_count=Count("recipes")
        )
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            paginated_queryset, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, pk=kwargs["id"])

        if request.method == "POST":
            serializer = SubscriptionsSerializer(
                author, data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=request.user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = Subscribe.objects.filter(
            user=request.user, author=author
        ).delete()
        if subscription[0] > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"Ошибка": "Вы не были подписаны на этого пользователя"},
            status=status.HTTP_400_BAD_REQUEST,
        )
