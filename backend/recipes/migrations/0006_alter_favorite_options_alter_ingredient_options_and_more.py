# Generated by Django 4.2.3 on 2023-08-22 22:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0005_alter_favorite_recipe_alter_favorite_user"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="favorite",
            options={
                "ordering": ["-pub_date"],
                "verbose_name": "Избранный",
                "verbose_name_plural": "Избранные",
            },
        ),
        migrations.AlterModelOptions(
            name="ingredient",
            options={
                "ordering": ["name"],
                "verbose_name": "Ингредиент",
                "verbose_name_plural": "Ингредиенты",
            },
        ),
        migrations.AlterModelOptions(
            name="shoppingcart",
            options={
                "verbose_name": "Корзина",
                "verbose_name_plural": "Корзины",
            },
        ),
        migrations.AlterModelOptions(
            name="tag",
            options={
                "ordering": ["name"],
                "verbose_name": "Тег",
                "verbose_name_plural": "Теги",
            },
        ),
        migrations.AlterField(
            model_name="ingredientsinrecipe",
            name="ingredient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ingredientsinrecipe",
                to="recipes.ingredient",
            ),
        ),
    ]
