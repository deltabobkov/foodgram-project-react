from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from core.models import CreatedModel

User = get_user_model()


class Tag(models.Model):
    """Модель тегов.

    Описывается следующими полями:

    name - Название тега.
    color - Цветовой HEX-код (например, #49B64E).
    slug - слаг тега.
    """

    name = models.CharField(
        "Название",
        unique=True,
        max_length=255,
    )
    color = models.CharField(
        "Цветовой HEX-код",
        unique=True,
    )
    slug = models.SlugField(
        "Уникальный слаг",
        unique=True,
        max_length=255,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]


class Ingredient(models.Model):
    """Модель ингридиентов.

    Данные об ингредиентах хранятся в нескольких связанных таблицах.
    Описывается следующими полями:

    name - Название.
    units - Единицы измерения.
    """

    name = models.CharField(
        "Название",
        max_length=255,
    )
    measurement_unit = models.CharField(
        "Единица измерения",
        max_length=15,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ["name"]


class Recipe(CreatedModel):
    """Модель для рецептов.

    Описывается следующими полями:

    author - Автор публикации (пользователь).
    name - Название.
    image - Картинка блюда.
    text - Текстовое описание рецепта.
    ingridients - Ингредиенты: продукты для приготовления блюда по рецепту.
    Множественное поле, выбор из предустановленного списка,
    с указанием количества и единицы измерения.
    tags - Теги (можно установить несколько тегов на один рецепт,
    выбор из предустановленных).
    cooking_time - Время приготовления в минутах.
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор рецепта",
        related_name="recipes",
    )
    name = models.CharField(
        "Название рецепта",
        max_length=255,
    )
    image = models.ImageField(
        "Изображение блюда",
        upload_to="recipes/",
        blank=True,
    )
    text = models.TextField(
        "Описание рецепта",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="recipes",
        verbose_name="Ингредиенты",
        through="IngredientsInRecipe",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
        related_name="recipes",
    )
    cooking_time = models.PositiveIntegerField(
        "Время приготовления",
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-pub_date"]

    def __str__(self):
        return self.name


class IngredientsInRecipe(models.Model):
    """Модель ингридиентов в рецепте.

    Описывается следующими полями:

    ingredient - Ингридиент из модели ингридиентов.
    amount - количество ингридиента.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipeingredient",
        verbose_name="Рецепт",
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredientsinrecipe",
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )

    def __str__(self):
        return f"{self.ingredient.name}: {self.amount}"


class ShoppingCart(CreatedModel):
    """Модель для корзины.

    Описывается следующими полями:

    user - Пользователь добавивший рецепт в корзину.
    recipe - Добавленный рецепт.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="shopping_cart"
    )

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="user_shopping_cart"
            )
        ]


class Favorite(CreatedModel):
    """Модель для избранных рецепт.

    Описывается следующими полями:

    user - Пользователь добавивший рецепт в избранное.
    recipe - Добавленный рецепт.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites",
    )

    class Meta:
        verbose_name = "Избранный"
        verbose_name_plural = "Избранные"
        ordering = ["-pub_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="user_recipe"
            )
        ]
