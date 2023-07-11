import csv

from django.conf import settings
from django.core.management import BaseCommand
from recipes.models import Ingredient


TABLE_DICT = {
    Ingredient: 'ingredients.csv',
}


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        for model, csv_f in TABLE_DICT.items():
            with open(
                f'{settings.BASE_DIR}/data/{csv_f}',
                'r',
                encoding='utf-8'
            ) as f:
                reader = csv.DictReader(f, delimiter=',')
                for row in reader:
                    name, measurement_unit = row
                    ingredient = Ingredient(name=name,
                                            measurement_unit=measurement_unit)
                    ingredient.save()
                print(f'Файл {f.name} загружен.')
