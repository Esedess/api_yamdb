from csv import DictReader
from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404

from reviews.models import Title, Review
from users.models import CustomUser

ALREDY_LOADED_ERROR_MESSAGE = """
Если необходимо снова загрузить данные из CSV файлов,
сначала удалите файо db.sqlite3 для очистки базы данных.
Затем запустите `python manage.py migrate` для создания пустой
базы данных с таблицами"""


class Command(BaseCommand):
    help = "Загружает данные из review.csv"

    def handle(self, *args, **options):
        if Review.objects.exists():
            print('данные уже загружены')
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return
        print('Загружаю данные')
        for row in DictReader(open('./static/data/review.csv')):
            title_obj = get_object_or_404(Title, id=row['title_id'])
            author_obj = get_object_or_404(CustomUser, id=row['author'])
            comment = Review(
                id=row['id'],
                title=title_obj,
                text=row['text'],
                author=author_obj,
                score=row['score'],
                pub_date=row['pub_date']
            )
            comment.save()
