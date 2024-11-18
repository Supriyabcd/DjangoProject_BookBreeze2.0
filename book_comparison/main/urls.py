from django.urls import path
from django.conf import settings  # Import settings here
from django.conf.urls.static import static  # Import static here
from django.contrib.auth import views as auth_views
from . import views
from .views import personal_details_view, category_selection_view, save_shelf_status

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('signup/', views.signup, name='signup'),
    path('books/', views.book_list, name='book_list'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('personal-details/', personal_details_view, name='personal_details'),
    path('category-selection/', category_selection_view, name='category_selection'),
    path('profile/', views.profile_view, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('update_progress/<int:pk>/', views.update_progress, name='update_progress'),
    path('save-shelf-status/', save_shelf_status, name='save_shelf_status'),
    path('book/<int:book_id>/rate/', views.rate_book, name='rate_book'),
    path('book/<int:pk>/review/', views.review_book, name='review_book'),
    path('book/<int:pk>/review/submit/', views.book_detail, name='book_detail'),
    path('bookshelf/<str:shelf_name>/', views.bookshelf_view, name='bookshelf'),
    #path('shelves/', views.shelf_list, name='shelf_list'),
    path('add_shelf/', views.add_shelf, name='add_shelf'),
    #path('shelves/<int:shelf_id>/add_book/<int:book_id>/', views.add_book_to_shelf, name='add_book_to_shelf'),
    #path('shelves/<int:shelf_id>/remove_book/<int:book_id>/', views.remove_book_from_shelf, name='remove_book_from_shelf'),
    #path('shelf/<int:shelf_id>/', views.bookshelf_view, name='custom_shelf'),
    path('profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('send_friend_request/<int:userID>/', views.send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:requestID>/', views.accept_friend_request, name='accept_friend_request'),
    path('add_friend/', views.search_users, name='add_friend'),  # URL for the search view
    path('accept_friend/', views.accept_friend, name='accept_friend'),  # URL to accept a friend request
    path('friends/', views.friends_list, name='friends_list'),
    path('chat/<int:friend_id>/', views.chat, name='chat'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
