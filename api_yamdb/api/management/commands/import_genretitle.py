from csv import DictReader
from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404

from reviews.models import GenreTitle, Title, Genre

ALREDY_LOADED_ERROR_MESSAGE = """
Если необходимо снова загрузить данные из CSV файлов,
сначала удалите файо db.sqlite3 для очистки базы данных.
Затем запустите `python manage.py migrate` для создания пустой
базы данных с таблицами"""


class Command(BaseCommand):
    help = "Загружает данные из genre_title.csv"

    def handle(self, *args, **options):
        if GenreTitle.objects.exists():
            print('данные уже загружены')
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return
        print('Загружаю данные')
        for row in DictReader(open('./static/data/genre_title.csv')):
            title_obj = get_object_or_404(Title, id=row['title_id'])
            genre_obj = get_object_or_404(Genre, id=row['genre_id'])
            genre_title = GenreTitle(
                id=row['id'],
                title=title_obj,
                genre=genre_obj
            )
            genre_title.save()
