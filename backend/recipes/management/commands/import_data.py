import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient

CSV_PATH = f'{settings.BASE_DIR}/data/ingredients.csv'


class Command(BaseCommand):
    """ Команда импорта данных из CSV-файла в БД."""
    def handle(self, *args, **options):
        with open(
            str(CSV_PATH), 'r', newline=''
        ) as file:
            reader = csv.DictReader(
                file, delimiter=',', fieldnames=['name', 'measurement_unit']
            )
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row['name'],
                    measurement_unit=row['measurement_unit']
                )

        self.stdout.write(self.style.SUCCESS(
            'Данные успешно загружены.'
        ))
