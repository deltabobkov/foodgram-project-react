# Generated by Django 4.2.3 on 2023-08-23 09:32

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0007_rename_units_ingredient_measurement_unit_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="recipe",
            old_name="coocking_time",
            new_name="cooking_time",
        ),
    ]
