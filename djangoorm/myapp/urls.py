from django.urls import path 
from . import views

urlpatterns = [
    path("",views.index,name='index'),
    path("library/",views.library,name='library'),
    path('get_author_books/<int:id>/',views.get_author_books,name='get_author_books'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('login_page/',views.login_page,name='login_page'),
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('user_reset_password/',views.user_reset_password,name='user_reset_password'),
    path('searchauthor/',views.search_author,name='search_author'),
    path('signup_page/',views.signup_page,name='signup_page'),
    path('user_register/',views.user_register,name='user_register'),
    path('user_login/',views.user_login,name='user_login'),
    path('user_logout/',views.user_logout,name='user_logout'),
    path('user_profile/',views.user_profile,name='user_profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('save_rating/<int:book_id>/',views.save_rating,name='save_rating'),
    path('get_rating/<int:book_id>/',views.get_rating,name='get_rating'),
    path('get_average_ratings/',views.get_average_ratings,name='get_average_ratings'),
    path('book/<int:book_id>/post_comments/', views.post_comments, name='post_comments'),
    path('show_all_comments/<int:book_id>/',views.show_all_comments, name='show_all_comments'),
    path('display_ratings_comments/<int:book_id>/',views.display_ratings_comments, name='display_ratings_comments'),
    path('all_ratings_for_book/<int:author_id>/',views.all_ratings_for_book,name='all_ratings_for_book'),
    path('rent_book/<int:book_id>/',views.rent_book,name='rent_book'),
    path('books_on_rent/<int:book_id>/',views.books_on_rent,name='books_on_rent'),
    path('get_notifications/',views.get_notifications,name='get_notifications'),
    path('get_book_status/',views.get_book_status,name='get_book_status'),
]