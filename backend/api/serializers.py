from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from django.db.models import F
from django.shortcuts import get_object_or_404

from recipes.models import (
    Favorite, Ingredient, IngredientsInRecipe, Recipe, ShoppingCart, Tag,
)
from users.models import Subscribe, User


class CreateUserSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=request.user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug", "color")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id", read_only=True)
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )
    amount = serializers.IntegerField(source="ingredient_amount")

    class Meta:
        model = IngredientsInRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsInRecipe
        fields = ("id", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class GetRecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values(
            "id",
            "name",
            "measurement_unit",
            amount=F("ingredientsinrecipe__amount"),
        )
        return ingredients

    def get_is_favorited(self, obj):
        return (
            self.context["request"].user.is_authenticated
            and Favorite.objects.filter(
                user=self.context["request"].user, recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
            self.context["request"].user.is_authenticated
            and ShoppingCart.objects.filter(
                user=self.context["request"].user, recipe=obj
            ).exists()
        )


class CreateRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    author = UserSerializer(read_only=True)
    ingredients = IngredientsInRecipeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError(
                {"ingredients": "Необходим хотя бы один ингридиент."}
            )
        ingredients_list = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=item["id"])
            if ingredient in ingredients_list:
                raise ValidationError(
                    {"ingredients": "Ингредиенты должны быть уникальными."}
                )
            if int(item["amount"]) < 1:
                raise ValidationError(
                    {"amount": "Минимальное количество ингредиента - 1."}
                )
            ingredients_list.append(ingredient)
        return value

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise ValidationError({"tags": "Выберите минимум 1 тег."})
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError({"tags": "Повторный тег."})
            tags_list.append(tag)
        return value

    def validate_cooking_time(self, value):
        cooking_time = value
        if cooking_time < 1:
            raise ValidationError(
                {"cooking_time": "Минимальное время - 1 минута"}
            )
        return value

    def create_ingredients(self, ingredients, recipe):
        IngredientsInRecipe.objects.bulk_create(
            [
                IngredientsInRecipe(
                    ingredient=Ingredient.objects.get(id=ingredient["id"]),
                    recipe=recipe,
                    amount=ingredient["amount"],
                )
                for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(recipe=instance, ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return GetRecipeSerializer(instance, context=context).data


class SubscriptionsSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(default=0)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        read_only_fields = ("email", "username", "first_name", "last_name")

    def get_recipes(self, obj):
        limit = self.context["request"].query_params.get("recipes_limit")
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        return RecipeSerializer(recipes, many=True).data

    def validate(self, data):
        author = self.instance
        user = self.context.get("request").user
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail="Вы уже подписаны на этого пользователя!",
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise ValidationError(
                detail="Вы не можете подписаться на самого себя!",
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data
