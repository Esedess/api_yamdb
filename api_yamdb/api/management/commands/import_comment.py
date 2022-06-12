from csv import DictReader
from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404

from reviews.models import Comment, Review
from users.models import CustomUser

ALREDY_LOADED_ERROR_MESSAGE = """
Если необходимо снова загрузить данные из CSV файлов,
сначала удалите файо db.sqlite3 для очистки базы данных.
Затем запустите `python manage.py migrate` для создания пустой
базы данных с таблицами"""


class Command(BaseCommand):
    help = "Загружает данные из comments.csv"

    def handle(self, *args, **options):
        if Comment.objects.exists():
            print('данные уже загружены')
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return
        print('Загружаю данные')
        for row in DictReader(open('./static/data/comments.csv')):
            review_obj = get_object_or_404(Review, id=row['review_id'])
            author_obj = get_object_or_404(CustomUser, id=row['author'])
            comment = Comment(
                id=row['id'],
                review=review_obj,
                text=row['text'],
                author=author_obj,
                pub_date=row['pub_date']
            )
            comment.save()
