from django.shortcuts import render,get_object_or_404,redirect
from .models import Author,Book,Reader,Carousals,CustomUser,Rating,Comment,Rental,Notification
from django.http import JsonResponse
from django.contrib.auth import login,logout,authenticate
from django.db.models import Q,Avg,Max
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import get_user_model
import datetime
from django.utils import timezone 


User = get_user_model()

def index(request):
    carousals = Carousals.objects.all()
    authors_data = Author.objects.all().order_by('name')
    paginator = Paginator(authors_data, 8) 
    page = request.GET.get('page')
    try:
        authors_data = paginator.page(page)
    except PageNotAnInteger:
        authors_data = paginator.page(1)
    except EmptyPage:
        authors_data = paginator.page(paginator.num_pages)
    data = {
        'authors_data': authors_data,
        'carousals': carousals,
    }
    return render(request, 'index.html',data)


def get_average_ratings(request):
    authors = Author.objects.all()
    data = []

    for author in authors:
        average_rating = author.books.aggregate(avg_rating=Avg('rating__rating'))['avg_rating'] or 0
        total_users_rating = Rating.objects.filter(book__author=author).values('user').distinct().count()
        data.append({'author_id': author.id, 'avg_rating': average_rating,'total_users_rating':total_users_rating})
    return JsonResponse(data, safe=False)


def search_author(request):
    authors_data = []
    error_message = ""
    if request.method == 'GET':
        search_content = request.GET.get('searchauthor',False)
        if search_content:
            authors_data = Author.objects.filter(Q(name__icontains=search_content))
            if not authors_data:
                error_message = "No authors found with the given search criteria."
        data = {
            'authors_data': authors_data,
            "error_message":error_message,
        }
    return render(request, 'index.html', data)
  
       
def login_page(request):
    return render(request, 'login.html') 
 
 
def signup_page(request):
    return render(request, 'signup.html')


def user_register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        name = email.split('@')[0] 
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        mobile = request.POST.get('mobile_number')

        if CustomUser.objects.filter(email=email).exists() or CustomUser.objects.filter(mobile_number=mobile).exists():
            error_message = "Email or mobile number is already registered."
            
        elif password != confirm_password:
            error_message = "Password and confirm password do not match."
            
        elif not mobile:
            error_message = "Mobile number is required."
            
        elif not mobile.isdigit():
            error_message = "Mobile number should contain only digits."
            
        elif len(mobile) != 10:
            error_message = "Mobile number should be 10 digits."
            
        else:
            user = CustomUser.objects.create_user(email=email, password=password,name=name)
            user.save()
            return render(request, 'signup.html', {'success_message':"User Registered Successfully"}) 
    return render(request, 'signup.html', {'error_message': error_message})

    
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not CustomUser.objects.filter(email=email).exists():
            error_message = "user not found for this email address"
            return render(request, 'login.html', {'error_message':error_message})
        
        # Authenticate the user
        user = authenticate(request, email=email, password=password)
        if user is not None:
            # allow user to login
            login(request,user)
            request.session.set_expiry(1200)
            return redirect('/')
        else:
            error_message = "Invalid password"
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')
    

def forgot_password(request):
    return render(request, 'forgot_password.html')


def user_reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        try:
            user = CustomUser.objects.get(email=email)
            if user:
                if password == confirm_password:
                    user.set_password(password)
                    user.save()
                    success_message = "password updated successfully"
                    return render(request, 'forgot_password.html', {'success_message':success_message}) 
                else:
                    error_message = "password doesn't matched"
                    return render(request, 'forgot_password.html', {'error_message':error_message}) 
                
            else:
                error_message = "user not found"
                return render(request, 'forgot_password.html', {'error_message':error_message}) 
        except Exception as e:
            error_message = "email is not registered with us"
            return render(request, 'forgot_password.html', {'error_message':error_message}) 
        
    return JsonResponse({'success': True})


def user_logout(request):
    logout(request)
    return redirect('index')  


@login_required 
def user_profile(request):
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'profile-data.html',context)

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        user.name = request.POST.get('name')
        user.age = request.POST.get('age')
        user.mobile_number = request.POST.get('contact')
        user.country = request.POST.get('country')
        user.city = request.POST.get('city')
        profile_pic = request.FILES.get('profile-pic')
        if profile_pic:
            user.profile_pic = profile_pic
        user.save()
        return render(request, 'profile-data.html', {'success_message':"Profile Updated"}) 
    
    return render(request, 'profile-data.html', {'error_message':"failed to update"}) 

    
def library(request):
    authors = Author.objects.all()
    data = []
    for author in authors:
        books = Book.objects.filter(author=author)
        readers = Reader.objects.filter(favorite_books__in=books)   
        author_data = {
            'author': author,
            'books': books,
            'readers': readers,
        }      
        data.append(author_data)
    context = {'data': data}
    return render(request, 'index.html', context)



def get_author_books(request,id):
    author_name = Author.objects.get(pk=id)
    get_books = Book.objects.filter(author=author_name)
    readers = Reader.objects.filter(favorite_books__in=get_books) 
    data = {
        'get_books': get_books, 
        'author_name': author_name.name,
        'bio':author_name.bio,
        'readers':readers,
        }
    return render(request, 'author_books.html',data)


@login_required
def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    content = book.book_content
    words_per_page = 200
    words = content.split()
    pages = [words[i:i + words_per_page] for i in range(0, len(words), words_per_page)]
    page = request.GET.get('page', 1)
    paginator = Paginator(pages, 2) 

    try:
        current_page = paginator.page(page)
    except PageNotAnInteger:
        current_page = paginator.page(1)
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)

    user = request.user
    user_comments = Comment.objects.filter(user=user, book=book)
    total_comments = Comment.objects.filter(book=book).count()

    try:
        rating = Rating.objects.get(user=user, book=book).rating
    except Rating.DoesNotExist:
        rating = None
    except Exception as e:
        rating = None  

    context = {
        'book': book,
        'current_page': current_page,
        'user_rating': rating,
        'user_comments': user_comments,
        'total_comments':total_comments,

    }
    return render(request, 'book_detail.html', context)


# @login_required
# def book_detail(request, book_id):
#     book = get_object_or_404(Book, pk=book_id)
#     content = book.book_content
#     words_per_page = 70
#     words = content.split()

#     # Split content into pages based on words_per_page
#     pages = [words[i:i + words_per_page] for i in range(0, len(words), words_per_page)]
#     context = {
#         'book': book,
#         'pages': pages,  # Pass the split content to the template
#         # Include any other context data you need
#     }
#     return render(request, 'book_detail.html', context)

@login_required
@require_POST
def save_rating(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    user = request.user
    rating_value = int(request.POST.get('rating', 0))
    if not book.book_content:  # if book content is empty then no comments...
        return JsonResponse({'success': False, 'error': "Can't Rate, book is not published yet."})
    try:
        rating_instance = Rating.objects.get(user=user, book=book)
        
        rating_instance.rating = rating_value
        rating_instance.save()

    except Rating.DoesNotExist:
        try:
            Rating.objects.create(user=user, book=book, rating=rating_value)
        except Exception as e:
            return JsonResponse({'success': False, 'error': 'Invalid rating value'})

    return JsonResponse({'success': True})


@login_required
@require_GET
def get_rating(request, book_id, book=None):
    book = get_object_or_404(Book, pk=book_id)
    user = request.user

    if Rating.objects.filter(user=user, book=book).exists():
        rating_instance = Rating.objects.get(user=user, book=book)
    else:
        rating_instance = None

    return JsonResponse({
        'rating': rating_instance.rating if rating_instance else None,
    })
    

@login_required
@require_POST
def post_comments(request, book_id):
    if request.method == 'POST':
        postcomment = request.POST.get('postcomment')
        book = get_object_or_404(Book, pk=book_id)
        user = request.user
        
        if not book.book_content:  # if book content is empty then no comments...
            messages.warning(request, "Can't comment, book is not published yet.")
        else:
            already_commented = Comment.objects.filter(user=user, book=book).exists()

            if already_commented:
                messages.warning(request, "You have already commented on this book.")
            else:
                try:
                    if postcomment:
                        comment = Comment.objects.create(
                            user=user,
                            book=book,
                            content=postcomment
                        )
                        messages.success(request, "Comment posted successfully")
                except Exception as e:
                    messages.success(request, "Error while posting comment")

    return redirect('book_detail', book_id=book_id)


@login_required
@require_GET
def show_all_comments(request, book_id):
    if request.method == 'GET':
        book = Book.objects.get(pk=book_id)
        # all_comments = Comment.objects.filter(book=book)
        # total_comments = all_comments.count()
        users_with_comments = CustomUser.objects.filter(comment__book=book).distinct()
        # print(users_with_comments)
        ratings = Rating.objects.filter(book=book).values('user__id', 'rating')
        users_with_ratings_for_book = list(ratings)
        # print(users_with_ratings_for_book)
        user_comments_dict = {}
        for user in users_with_comments:
            user_comments = Comment.objects.filter(user=user, book=book)
            user_comments_dict[user] = user_comments
        
        context = {
            'book': book,
            'user_comments_dict': user_comments_dict,
            'users_with_ratings_for_book':users_with_ratings_for_book,
        }
    return render(request, 'all_comments.html', context)


@login_required
@require_GET
def display_ratings_comments(request, book_id):
    if request.method == 'GET':
        book = Book.objects.get(pk=book_id)
        ratings = Rating.objects.filter(book=book).values('book__id','user__id', 'rating')   
        users_with_ratings_for_book = list(ratings)
        context = {
            'users_with_ratings_for_book': users_with_ratings_for_book,
        }
    return JsonResponse(context)


@require_GET
def all_ratings_for_book(request, author_id):
    if request.method == 'GET':
        try:
            books_with_average_ratings = Book.objects.filter(author_id=author_id) \
                .annotate(average_rating=Avg('rating__rating')) \
                .values('id', 'average_rating')

            ratings_for_books = {book['id']: book['average_rating'] for book in books_with_average_ratings}

            context = {'ratings_for_books': ratings_for_books}
            return JsonResponse(context)

        except (Author.DoesNotExist,Book.DoesNotExist) as e:
            return JsonResponse({'message_error': 'Author or book does not exist'})
        except Exception as e:
            return JsonResponse({'message_error': str(e)})
                
    return JsonResponse({'message_error': 'something went wrong'})


def rent_book(request,book_id):
    book = Book.objects.get(id=book_id)
    context={'book':book}
    return render(request,'rent_book.html',context)


def books_on_rent(request, book_id):
    if request.method == 'POST':
        user = request.user
        book = get_object_or_404(Book, id=book_id)
        rent_duration = request.POST.get('rent-duration')
        rented_token = request.POST.get('rented-token')
        
        # Check the count of books rented by the user
        rented_books_count = Rental.get_rented_books_count_for_user(user)
        if rented_books_count >= 2:
            messages.warning(request, "You have already rented two books. Return a book to rent another.")
            return redirect('rent_book', book_id=book_id)

        if rent_duration and rented_token:
            if not book.book_content:  # Check if book content is empty
                messages.warning(request, "This book has not been published by the author yet")
                return redirect('rent_book', book_id=book_id)
            try:
                rent_out_book = Rental.objects.get(user=user, book=book, returned=False)
                messages.error(request, "You have already rented this book.")
            except Rental.DoesNotExist:
                rent_out_book = Rental(user=user, book=book, rented_token=rented_token)
                rent_out_book.rented_date = timezone.now()

                rent_out_book.return_date = rent_out_book.rented_date + datetime.timedelta(days=int(rent_duration))
                rent_out_book.save()

                messages.success(request, "Book rented successfully")
        else:
            messages.error(request, "Please provide valid rent duration and token")

    return redirect('rent_book', book_id=book_id)


@login_required
def get_notifications(request):
    if request.user.is_authenticated:
        user_id = request.user.id  # Get the user ID of the logged-in user
        # Filter notifications for the specific user
        notifications = Notification.objects.filter(user_id=user_id)
        notifications_data = []
        for notification in notifications:
            notification_data = {
                'user_id': notification.user_id,
                'message': notification.message,
                'day_left': notification.day_left
            }
            notifications_data.append(notification_data)
        print("Notification data===",notifications_data)
        return JsonResponse(notifications_data, safe=False)
    else:
        return JsonResponse([], safe=False)
    

def get_book_status(request):
    return render(request,'book_status.html')