from csv import DictReader
from django.core.management.base import BaseCommand

from reviews.models import Categorу

ALREDY_LOADED_ERROR_MESSAGE = """
Если необходимо снова загрузить данные из CSV файлов,
сначала удалите файо db.sqlite3 для очистки базы данных.
Затем запустите `python manage.py migrate` для создания пустой
базы данных с таблицами"""


class Command(BaseCommand):
    help = "Загружает данные из category.csv"

    def handle(self, *args, **options):
        if Categorу.objects.exists():
            print('данные уже загружены')
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return
        print('Загружаю данные')
        for row in DictReader(open('./static/data/category.csv')):
            category = Categorу(
                name=row['name'],
                slug=row['slug']
            )
            category.save()
