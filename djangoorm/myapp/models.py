from django.db import models
from faker import Faker
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin,Group,Permission
fake = Faker()

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=128,default='')
    age = models.PositiveIntegerField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    mobile_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    country = models.CharField(max_length=100,default='',blank=False)
    city = models.CharField(max_length=100,default='',blank=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()
    
    groups = models.ManyToManyField(Group, verbose_name='Groups', blank=True, related_name='custom_user_set')
    user_permissions = models.ManyToManyField(Permission, verbose_name='User Permissions', blank=True, related_name='custom_user_set')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Carousals(models.Model):
    image1 = models.ImageField(upload_to='carousals/photos')
    image2 = models.ImageField(upload_to='carousals/photos')
    image3 = models.ImageField(upload_to='carousals/photos')
    
    class Meta:
      verbose_name_plural = "Carousals"  
    

class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()
    author_pic = models.ImageField(upload_to='author/photos/',default=None,null=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE,related_name='books')
    genre = models.CharField(max_length=50)
    published_year = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    book_content = models.TextField(default='')

    def __str__(self):
        return self.title


class Reader(models.Model):
    name = models.CharField(max_length=100)
    favorite_books = models.ManyToManyField(Book, related_name='readers')

    def __str__(self):
        return self.name
    

class ContactMessage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.user.name}"
    
    
class Rating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])

    def __str__(self):
        return f"{self.user.email} rated {self.book.title} with {self.rating} stars"


class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=250,blank=False,null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.name} on {self.book.title}"


class Rental(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rented_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField()
    returned = models.BooleanField(default=False)
    rented_token = models.DecimalField(max_digits=8, decimal_places=2)
    
    @classmethod
    def get_rented_books_count_for_user(cls, user):
        return cls.objects.filter(user=user, returned=False).count()
    
    def __str__(self) -> str:
        return f"{self.book.title} rented by {self.user.name} on {self.rented_date}"
    
    
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True,default='')
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE,null=True,default='')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    day_left = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.email} - {self.message}"

    def save(self, *args, **kwargs):
        # Retrieve the latest rental for the associated user
        latest_rental = Rental.objects.filter(user=self.user).latest('rented_date')
        
        # Calculate and save days left based on the latest rental
        if latest_rental:
            days_left = (latest_rental.return_date - timezone.now()).days
            self.day_left = days_left if days_left > 0 else 0

        super().save(*args, **kwargs)
        
        
# import random
# def create_author():
#     author = Author.objects.create(
#         name=fake.name(),
#         bio=fake.paragraph(),
#     )
#     return author

# def create_book(author):
#     book = Book.objects.create(
#         title=fake.catch_phrase(),
#         author=author,
#         genre=fake.word(),
#         published_year=fake.year(),
#         price=random.uniform(10, 100),  # Generating a random price between 10 and 100
#         book_content=fake.text(),
#     )
#     return book

# def create_reader():
#     reader = Reader.objects.create(
#         name=fake.name(),
#     )
#     return reader

# # Create 20 authors
# for _ in range(20):
#     author = create_author()
    
#     # Create 10 books for each author
#     for _ in range(10):
#         create_book(author)

# # Create 5 readers
# for _ in range(5):
#     reader = create_reader()
    
#     # Get 5 random books and add them as favorite books for the reader
#     random_books = Book.objects.order_by('?')[:5]
#     reader.favorite_books.add(*random_books)