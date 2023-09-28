import csv
from recipes.models import Ingredient, Tag

from django.core.management.base import BaseCommand

CSV_PATH = 'static/data/'
FOREIGN_KEY_FIELDS = ('name')

DICT = {
    Ingredient: 'ingredients.csv',
    Tag: 'tags.csv'
}


def csv_import(csv_data, model):
    objects = []
    for row in csv_data:
        for field in FOREIGN_KEY_FIELDS:
            if field in row:
                row[f'{field}'] = row[field]
                del row[field]
        objects.append(model(**row))
    model.objects.bulk_create(objects)


class Command(BaseCommand):
    help = 'Импортирует данные из файла CSV в модель.'

    def handle(self, *args, **kwargs):
        for model in DICT:
            with open(
                CSV_PATH + DICT[model],
                newline='',
                encoding='utf8'
            ) as csv_file:
                csv_import(csv.DictReader(csv_file), model)
        self.stdout.write(
            self.style.SUCCESS(
                'Загрузка завершена'
            )
        )
