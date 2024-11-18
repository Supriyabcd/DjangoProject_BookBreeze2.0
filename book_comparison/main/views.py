from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, UserProfile, Genre, BookList, Rating, Review, Shelf, Friend_Request, Message
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import PersonalDetailsForm, EditProfileForm, ShelfForm
from .forms import CategorySelectionForm, UpdateProgressForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db.models import Count, Q
from django.utils import timezone

@csrf_protect
def category_selection_view(request):
    user_profile = UserProfile.objects.get(user=request.user)  # Get the user's profile
    if request.method == 'POST':
        form = CategorySelectionForm(request.POST)
        if form.is_valid():
            selected_genres = request.POST.getlist('genres')  # 'genres' now refers to Genre model
            # Clear previous selections, if any, to avoid duplicates
            user = request.user
            user_profile.genres.set(selected_genres)  # Use set() to update the many-to-many field
            user_profile.save()

            return redirect('book_list')  # Redirect to book_list after selection
    else:
        form = CategorySelectionForm()

    genres = Genre.objects.all()  # Fetch all genres from the Genre model

    return render(request, 'category_selection.html', {
        'form': form,
        'selected_genres': genres  # Pass the genres to the template
    })

    
def personal_details_view(request):
    if request.method == 'POST':
        form = PersonalDetailsForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            return redirect('category_selection')  # Redirect to the next step
    else:
        form = PersonalDetailsForm()

    return render(request, 'personal_details.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Log the user in after sign-up
            # In your signup view
            if UserProfile.objects.filter(user=user).exists():
                return redirect('book_list')  # If the user profile exists, redirect them to book_list
            else:
                return redirect('personal_details')  # Otherwise, redirect to personal details

    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def home(request):
    return render(request, 'home.html')

@login_required
def book_list(request):
    books = Book.objects.all()
    latest_books = Book.objects.order_by('-release_date')
    fiction_books = Book.objects.filter(genres__name="Fiction").order_by('-release_date')
    nonfiction_books = Book.objects.filter(genres__name="Nonfiction").order_by('-release_date')

    context = {
        'latest_books': latest_books,
        'fiction_books': fiction_books,
        'nonfiction_books': nonfiction_books,
    }
    return render(request, 'book_list.html', context)
    
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    user = request.user

    # Get the user's rating for the book if it exists
    user_rating = None
    if request.user.is_authenticated:
        try:
            user_rating = Rating.objects.get(book=book, user=request.user).rating
        except Rating.DoesNotExist:
            user_rating = None  # User has not rated this book yet

    # Get the average rating
    book.average_rating = book.get_average_rating(exclude_user=request.user)
    
    # Calculate the percentage width for the stars based on the average rating
    filled_stars_percentage = (book.average_rating / 5.0) * 100

    # Get the number of people currently reading this book
    currently_reading_count = book.get_currently_reading_count(exclude_user=request.user)
    want_to_read_count = book.get_want_to_read_count(exclude_user=request.user)

    total_ratings = Rating.objects.filter(book=book).count()
    total_reviews = Review.objects.filter(book=book).count()
    
    # Calculate the breakdown of each rating (1 to 5 stars)
    ratings_count = (
        Rating.objects.filter(book=book)
        .values('rating')
        .annotate(count=Count('rating'))
        .order_by('-rating')
    )

    # Initialize rating breakdown dictionary
    rating_breakdown = {5: {'count': 0, 'percentage': 0},
                        4: {'count': 0, 'percentage': 0},
                        3: {'count': 0, 'percentage': 0},
                        2: {'count': 0, 'percentage': 0},
                        1: {'count': 0, 'percentage': 0}}

    # Fill the dictionary with actual counts and calculate percentages
    for entry in ratings_count:
        rating = entry['rating']
        count = entry['count']
        percentage = (count / total_ratings * 100) if total_ratings > 0 else 0
        rating_breakdown[rating]['count'] = count
        rating_breakdown[rating]['percentage'] = round(percentage)


    # Get the logged-in user's review
    user_review = Review.objects.filter(user=user, book=book).first()
    # Use the new method to get reviews from other users
    other_reviews = Review.get_others_reviews(book=book, exclude_user=user)

    # Assuming you have a ManyToMany relationship for genres
    related_books = Book.objects.filter(genres__in=book.genres.all()).exclude(id=book.id).distinct()

    context = {
        'book': book,
        'related_books': related_books,
        'user_rating': user_rating,
        'average_rating': book.average_rating,  # Keep this to display the actual rating value
        'filled_stars_percentage': filled_stars_percentage,  # Pass the percentage to the template
        'currently_reading_count': currently_reading_count,
        'want_to_read_count': want_to_read_count,
        'total_ratings': total_ratings,
        'total_reviews': total_reviews,
        'rating_breakdown': rating_breakdown,
        'user_review': user_review,
        'other_reviews': other_reviews,
    }

    return render(request, 'book_detail.html', context)

def rate_book(request, book_id):
    if request.method == 'POST':
        rating_value = int(request.POST.get('rating'))
        book = get_object_or_404(Book, id=book_id)
        user = request.user

        # Check if user has already rated the book
        rating, created = Rating.objects.get_or_create(user=user, book=book)
        rating.rating = rating_value
        rating.save()

        # Add the book to the "read" shelf if not already there
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        if book in user_profile.want_to_read.all():
            user_profile.want_to_read.remove(book)
        if book in user_profile.currently_reading.all():
            user_profile.currently_reading.remove(book)
        if book not in user_profile.read.all() and book not in user_profile.want_to_read.all() and book not in user_profile.currently_reading.all():
            user_profile.read.add(book)

        return HttpResponseRedirect(reverse('book_detail', args=[book_id]))

    return redirect('book_detail', book_id=book_id)

def review_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    user = request.user

    if request.method == 'POST':
        review_text = request.POST.get('review', '').strip()

        if review_text:  # Only proceed if the review is not empty
            # Save or update the review
            review, created = Review.objects.get_or_create(user=user, book=book)
            review.review = review_text
            review.save()

            # Update user profile shelves
            user_profile, _ = UserProfile.objects.get_or_create(user=user)

            # Remove from other shelves if present
            user_profile.want_to_read.remove(book)
            user_profile.currently_reading.remove(book)

            # Add to "read" shelf if not already there
            if book not in user_profile.read.all():
                user_profile.read.add(book)

            # Optional: Set a message to inform the user of successful submission
            messages.success(request, "Your review has been saved.")

            return HttpResponseRedirect(reverse('book_detail', args=[pk]))
        else:
            # Optional: Set a message for an empty review
            messages.error(request, "Review cannot be empty.")

            return redirect('book_detail', pk=book.pk)

    # Pass existing review for the book if it exists
    context = {
        'book': book,
        'previous_review': Review.objects.filter(user=user, book=book).first(),
    }

    return render(request, 'book_review.html', context)

#SUPRIYA#
@login_required
def profile_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)  # Fetch the UserProfile instance linked to the user

    # Retrieve shelves and books using the user_profile relationships
    default_shelves = Shelf.objects.filter(user_profile=user_profile, category__in=['to_read', 'currently_reading', 'read'])
    custom_shelves = Shelf.objects.filter(user_profile=user_profile, category='custom')
    book_list_entries = BookList.objects.filter(user_profile=user_profile, list_type='currently_reading').select_related('book_item')

    # Use counts for each shelf
    read_count = user_profile.read.count()
    currently_reading_count = user_profile.currently_reading.count()
    to_read_count = user_profile.want_to_read.count()
    currently_reading_books = user_profile.currently_reading.all()

    context = {
        'user_profile': user_profile,
        'default_shelves': default_shelves,
        'custom_shelves': custom_shelves,
        'book_list_entries': book_list_entries,
        'read_count': read_count,
        'currently_reading_count': currently_reading_count,
        'to_read_count': to_read_count,
        'currently_reading_books': currently_reading_books,
    }

    return render(request, 'profile.html', context)
    # if user_profile:
    #     # Query using user_profile where needed, rather than request.user
    #     books_currently_reading = Shelf.objects.filter(
    #         user_profile=user_profile, category='currently_reading'
    #     ).select_related('user_profile')
        
       
    #     # Fetch default and custom shelves
    #     default_shelves = Shelf.objects.filter(user_profile=user_profile, category__in=['to_read', 'currently_reading', 'read'])
    #     custom_shelves = Shelf.objects.filter(user_profile=user_profile, category='custom')

    #     book_list_entries = BookList.objects.filter(
    #         user_profile=user_profile, list_type='currently_reading'
    #     ).select_related('book_item')

    #     # Use counts on user_profile relationships
    #     read_count = user_profile.read.count()
    #     currently_reading_count = user_profile.currently_reading.count()
    #     to_read_count = user_profile.want_to_read.count()
    #     currently_reading_books = user_profile.currently_reading.all()

    #     context = {
    #         'user_profile': user_profile,
    #         'books_currently_reading': books_currently_reading,
    #         'book_list_entries': book_list_entries,
    #         'default_shelves': default_shelves,
    #         'custom_shelves': custom_shelves,
    #         'read_count': read_count,
    #         'currently_reading_count': currently_reading_count,
    #         'to_read_count': to_read_count,
    #         'currently_reading_books': currently_reading_books,
    #     }
    # else:
    #     # Optional: handle the case where no user profile exists
    #     context = {
    #         'error': 'User profile not found.',
    #     }

    # return render(request, 'profile.html', context)


@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the profile page after saving
    else:
        form = EditProfileForm(instance=user_profile)

    return render(request, 'edit_profile.html', {'form': form})

#SUPRIYA#
@login_required
def update_progress(request, pk):
    user_profile = request.user.userprofile
    book_list_entry = get_object_or_404(BookList, book_item__id=pk, user_profile=user_profile)

    if request.method == 'POST':
        form = UpdateProgressForm(request.POST)
        if form.is_valid():
            pages_read = form.cleaned_data['pages_read']
            total_pages = book_list_entry.book_item.total_pages
            percentage_read = min((pages_read / total_pages) * 100, 100)  # Calculate progress
            book_list_entry.progress = round(percentage_read, 2)  # Save the rounded percentage
            book_list_entry.pages_read = pages_read  # Save pages read for future reference
            book_list_entry.save()

            # Add the book to the list after updating progress
            add_book_to_list(user_profile, book_list_entry.book_item)

            messages.success(request, f'Progress updated to {book_list_entry.progress:.2f}%')
            # return redirect(reverse('book_detail',kwargs={'pk': pk})) # Redirect to book detail page

    else:
        form = UpdateProgressForm(initial={'pages_read': book_list_entry.pages_read})

    return render(request, 'update_progress.html', {'form': form, 'book_list_entry': book_list_entry})

#SUPRIYA#
@login_required
def add_shelf(request):
    if request.method == 'POST':
        form = ShelfForm(request.POST)
        if form.is_valid():
            new_shelf = form.save(commit=False)
            new_shelf.user_profile = request.user.userprofile
            new_shelf.category = 'custom' 
            new_shelf.is_default = False
            new_shelf.save()
            form.save_m2m()
            return redirect('profile')
    else:
        form = ShelfForm()
    return render(request, 'add_shelf.html', {'form': form})

#SUPRIYA#
@login_required
def save_shelf_status(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        shelf_id = request.POST.get('shelf')
        user_profile = request.user.userprofile  # Assuming the user is logged in

        # # Get the user's profile
        # user_profile = get_object_or_404(UserProfile, user=user)
        book = get_object_or_404(Book, id=book_id)

        user_profile.want_to_read.remove(book)  # Remove from 'Want to Read'
        user_profile.currently_reading.remove(book)  # Remove from 'Currently Reading'
        user_profile.read.remove(book)

        # # Process the form to save to the appropriate shelf
        # if shelf == 'want_to_read':
        #     #user_profile.want_to_read = user_profile.want_to_read or []
        #     #if book not in user_profile.want_to_read:
        #         user_profile.want_to_read.add(book)
        # elif shelf == 'currently_reading':
        #     #user_profile.currently_reading = user_profile.currently_reading or []
        #     #if book not in user_profile.currently_reading:
        #         user_profile.currently_reading.add(book)
        # elif shelf == 'read':
        #     #user_profile.read = user_profile.read or []
        #     #if book not in user_profile.read:
        #         user_profile.read.add(book)
        # Check if shelf_id is one of the predefined categories or a custom shelf

        # Add the book to the selected shelf or a custom shelf
        if shelf_id in ['want_to_read', 'currently_reading', 'read']:
            getattr(user_profile, shelf_id).add(book)
        else:
            custom_shelf = get_object_or_404(Shelf, id=shelf_id, user_profile=user_profile)
            custom_shelf.books.add(book)
        # Save the updated profile
        user_profile.save()

        # Add the book to the list after changing its shelf status
        add_book_to_list(user_profile, book)

        # Redirect back to the book detail page or another URL
        return redirect(reverse('book_detail', args=[book_id]))

    # If the request is not POST, redirect back to book list page
    return redirect(reverse('book_list'))

#SUPRIYA#
@login_required
def bookshelf_view(request, shelf_name):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if shelf_name == 'read':
        books = user_profile.read.all()
    elif shelf_name == 'currently_reading':
        books = user_profile.currently_reading.all()
    elif shelf_name == 'to_read':
        books = user_profile.want_to_read.all()
    else:
        shelf = get_object_or_404(Shelf, name=shelf_name, user_profile=user_profile)
        books = shelf.books.all()  # Custom shelf books

    context = {
        'user_profile': user_profile,
        'books': books,
        'shelf_name': shelf_name,
    }
    return render(request, 'bookshelf.html', context)

#SUPRIYA#
def write_review(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    # Add logic to handle the review form and save the review here.
    return render(request, 'write_review.html', {'book': book})



def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'user_profile.html', {'user': user})

@login_required
def send_friend_request(request, userID):
    from_user = UserProfile.objects.get(user=request.user)  # Get UserProfile of the logged-in user
    to_user = get_object_or_404(UserProfile, id=userID)     # Target user's UserProfile
    friend_request, created = Friend_Request.objects.get_or_create(from_user=from_user, to_user=to_user)
    if created:
        return HttpResponse('friend request sent')
    else:
        return HttpResponse('friend request was already sent')
    
@login_required
def accept_friend_request(request, requestID):
    friend_request = get_object_or_404(Friend_Request, id=requestID)
    if friend_request.to_user == UserProfile.objects.get(user=request.user):
        friend_request.to_user.friends.add(friend_request.from_user)
        friend_request.from_user.friends.add(friend_request.to_user)
        friend_request.delete()
        return HttpResponse('friend request accepted')
    else:
        return HttpResponse('friend request not accepted')
    
def search_users(request):
    query = request.GET.get('query')
    search_results = []
    if query:
        search_results = UserProfile.objects.filter(user__username__icontains=query)
    return render(request, 'add_friend.html', {'search_results': search_results, 'query': query})

def accept_friend(request):
    """Displays a list of friend requests sent to the logged-in user."""
    user_profile = UserProfile.objects.get(user=request.user)
    friend_requests = Friend_Request.objects.filter(to_user=user_profile)
    context = {
        'friend_requests': friend_requests
    }
    return render(request, 'accept_friend.html', context)

@login_required
def friends_list(request):
    user_profile = request.user.userprofile
    friends = user_profile.friends.all()
    context = {'friends': friends}
    return render(request, 'friends_list.html', context)

@login_required
def chat(request, friend_id):
    friend = get_object_or_404(UserProfile, id=friend_id)
    user_profile = UserProfile.objects.get(user=request.user)
    if friend not in user_profile.friends.all():
        return HttpResponse("You are not friends with this user")
    
    messages = Message.objects.filter(
        (Q(sender=user_profile) & Q(recipient=friend)) |
        (Q(sender=friend) & Q(recipient=user_profile))
    ).order_by('timestamp')

    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Message.objects.create(sender=user_profile, recipient=friend, content=content)
            return redirect('chat', friend_id=friend_id)

    return render(request, 'chat.html', {'friend': friend, 'messages': messages})

def add_book_to_list(user_profile, book):
    booklist, created = BookList.objects.get_or_create(user_profile=user_profile, book_item=book)
    if created:
        print("Book added to list.")
    else:
        print("Book already exists in the list.")

