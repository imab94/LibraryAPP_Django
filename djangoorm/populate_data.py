from myapp.models import *
import random

def create_author():
    author = Author.objects.create(
        name=fake.name(),
        bio=fake.paragraph(),
    )
    return author

def create_book(author):
    book = Book.objects.create(
        title=fake.catch_phrase(),
        author=author,
        genre=fake.word(),
        published_year=fake.year(),
        price=random.uniform(10, 100),  # Generating a random price between 10 and 100
        book_content=fake.text(),
    )
    return book

def create_reader():
    reader = Reader.objects.create(
        name=fake.name(),
    )
    return reader

# Create 20 authors
for _ in range(20):
    author = create_author()
    
    # Create 10 books for each author
    for _ in range(10):
        create_book(author)

# Create 5 readers
for _ in range(5):
    reader = create_reader()
    
    # Get 5 random books and add them as favorite books for the reader
    random_books = Book.objects.order_by('?')[:5]
    reader.favorite_books.add(*random_books)