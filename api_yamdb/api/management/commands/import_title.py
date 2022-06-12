from csv import DictReader
from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404

from reviews.models import Title, Categorу

ALREDY_LOADED_ERROR_MESSAGE = """
Если необходимо снова загрузить данные из CSV файлов,
сначала удалите файо db.sqlite3 для очистки базы данных.
Затем запустите `python manage.py migrate` для создания пустой
базы данных с таблицами"""


class Command(BaseCommand):
    help = "Загружает данные из titles.csv"

    def handle(self, *args, **options):
        if Title.objects.exists():
            print('данные уже загружены')
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return
        print('Загружаю данные')
        for row in DictReader(open('./static/data/titles.csv')):
            category_obj = get_object_or_404(Categorу, id=row['category'])
            title = Title(
                id=row['id'],
                name=row['name'],
                year=row['year'],
                category=category_obj
            )
            title.save()
