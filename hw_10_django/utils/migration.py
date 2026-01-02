import os
import sys
import django
from pymongo import MongoClient

sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quotes_toscrape.settings')
django.setup()

from quotes.models import Author, Quote, Tag

client = MongoClient("mongodb+srv://Bohdan:qwerty067@cluster0.c5ifxzn.mongodb.net/?appName=Cluster0")
db = client.hw8

def migrate():
    print("Migrating authors...")
    authors = db.authors.find()
    for a in authors:
        Author.objects.get_or_create(
            fullname=a['fullname'],
            defaults={
                'born_date': a.get('born_date', ''),
                'born_location': a.get('born_location', ''),
                'description': a.get('description', '')
            }
        )

    print("Migrating quotes...")
    quotes = db.quotes.find()
    for q in quotes:
        author_ref = q.get('author')
        if not author_ref:
            continue

        if isinstance(author_ref, object) and not isinstance(author_ref, str):
            mongo_author = db.authors.find_one({"_id": author_ref})
            author_name = mongo_author['fullname'] if mongo_author else None
        else:
            author_name = author_ref

        if author_name:
            pg_author = Author.objects.filter(fullname=author_name).first()
            if pg_author:
                quote_obj, _ = Quote.objects.get_or_create(quote=q['quote'], author=pg_author)

                for tag_name in q.get('tags', []):
                    tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                    quote_obj.tags.add(tag_obj)

if __name__ == '__main__':
    migrate()
    print("Done!")