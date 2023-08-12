import csv

from recipes.models import Ingredient

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with open("recipes/data/ingredients.csv", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            for row in reader:
                Ingredient.objects.get_or_create(name=row[0], units=row[1])
