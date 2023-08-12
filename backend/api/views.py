from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientsInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from users.models import Subscribe, User

from .filters import RecipeFilter
from .permissions import IsOwnerOrAdminOrReadOnly
from .serializers import (
    CreateRecipeSerializer,
    GetRecipeSerializer,
    IngredientSerializer,
    RecipeSerializer,
    SubscriptionsSerializer,
    TagSerializer,
    UserSerializer,
)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsOwnerOrAdminOrReadOnly,)


class TagViewSet(ReadOnlyModelViewSet):
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
            created = Favorite.objects.get_or_create(
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
        if request.method == "DELETE":
            obj = get_object_or_404(
                Favorite, user=request.user, recipe=recipe
            ).delete()
            if obj > 0:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"Ошибка": "Рецепт отсутствует в избранном"},
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
            created = ShoppingCart.objects.get_or_create(
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
        if request.method == "DELETE":
            obj = get_object_or_404(
                ShoppingCart, user=request.user, recipe=recipe
            ).delete()
            if obj > 0:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"Ошибка": "Рецепт отсутствует в списке покупок"},
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
        content = "Список покупок:\n\n"
        for ingredient in ingredients:
            name = ingredient.get("ingredient__name")
            measurement_unit = ingredient.get("ingredient__measurement_unit")
            amount = ingredient.get("amount")
            content += f"{name} ({measurement_unit}) - {amount}\n"
        response = HttpResponse(content, content_type="text/plain")
        response["Content-Disposition"] = 'attachment; filename="shoplist.txt"'
        return response


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get("id")
        author = get_object_or_404(User, id=author_id)

        if request.method == "POST":
            serializer = SubscriptionsSerializer(
                author, data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            get_object_or_404(
                Subscribe, user=request.user, author=author
            ).delete()
            return Response(
                {"errors": "Вы отписаны от этого автора."},
                status=status.HTTP_204_NO_CONTENT,
            )

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            paginated_queryset, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)
