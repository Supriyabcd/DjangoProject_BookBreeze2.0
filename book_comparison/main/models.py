from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.db.models import Avg
from django.utils import timezone

class Genre(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    genres = models.ManyToManyField(Genre)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True)
    published_date = models.DateField(null=True, blank=True)
    release_date = models.DateField(auto_now_add=True) 
    total_pages = models.IntegerField(null=True, blank=True)
    average_rating = models.FloatField(null=True, blank=True)

        
    def get_average_rating(self, exclude_user=None):
        ratings = self.ratings.all()  # All ratings for the book

        # If a user is specified to be excluded, filter out their rating
        if exclude_user:
            ratings = ratings.exclude(user=exclude_user)

        # Calculate the average rating
        average = ratings.aggregate(Avg('rating'))['rating__avg']

        # Return 0 if no ratings exist
        return round(average, 1) if average is not None else 0.0
    
    def get_currently_reading_count(self, exclude_user=None):
        currently_reading_users = self.currently_reading_users.all()  # All currently_reading_users for the book

        # If a user is specified to be excluded, filter out them
        if exclude_user:
            currently_reading_users = currently_reading_users.exclude(user=exclude_user)

        # Calculate the total count
        count = currently_reading_users.count()

        # Return 0 if count is 0
        return count if count is not None else 0
    
    def get_want_to_read_count(self, exclude_user=None):
        want_to_read_users = self.want_to_read_users.all()  # All want_to_read_users for the book

        # If a user is specified to be excluded, filter out their rating
        if exclude_user:
            want_to_read_users = want_to_read_users.exclude(user=exclude_user)

        # Calculate the average rating
        count = want_to_read_users.count()

        # Return 0 if no want_to_read_users exist
        return count if count is not None else 0
    
    def __str__(self):
        return self.title
    
    
class Price(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='prices')
    website = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.website}: {self.price}"
    
    
class Rating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(null=True, blank=True)  # Values from 1 to 5

    def __str__(self):
        return f"{self.user.username} rated {self.book.title} {self.rating} stars"
    

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.TextField()  

    @classmethod
    def get_others_reviews(cls, book, exclude_user=None):
        """
        Fetch reviews for a specific book, excluding the review by the specified user.
        """
        other_users_reviews = cls.objects.filter(book=book)
        
        if exclude_user:
            other_users_reviews = other_users_reviews.exclude(user=exclude_user)
        
        return other_users_reviews

    def __str__(self):
        return f"{self.user.username} reviewed {self.book.title} "
    


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    profession = models.CharField(max_length=100)
    languages = models.CharField(max_length=200)
    genres = models.ManyToManyField(Genre)   
    want_to_read = models.ManyToManyField(Book, related_name='want_to_read_users', blank=True)
    currently_reading = models.ManyToManyField(Book, related_name='currently_reading_users', blank=True)
    read = models.ManyToManyField(Book, related_name='read_users', blank=True)
    friends = models.ManyToManyField('self', blank=True)

    # def add_to_currently_reading(self, book):
    #     self.currently_reading.add(book)
    #     book.date_added = timezone.now()  # Set date added
    #     book.save()

        # Ensure there's a BookList entry for this book
    #     book_list_entry, created = BookList.objects.get_or_create(
    #         user_profile=self,
    #         book_item=book,
    #         defaults={'list_type': 'currently_reading', 'added_at': timezone.now()}
    #     )
    #     if not created:
    #         # Update if it already exists but was previously in another list
    #         book_list_entry.list_type = 'currently_reading'
    #         book_list_entry.last_accessed = timezone.now()
    #         book_list_entry.save()

    # # def remove_from_currently_reading(self, book):
    # #     self.currently_reading.remove(book)
        
    #     # Optionally remove the BookList entry, or set it to 'want_to_read' or 'read' if required
    #     BookList.objects.filter(user_profile=self, book_item=book, list_type='currently_reading').delete()

    def __str__(self):
        return self.user.username
    
    def add_to_shelf(self, book, shelf_type):
        """
        Adds a book to a specified shelf (want_to_read, currently_reading, read)
        and updates or creates a BookList entry.
        """
        if shelf_type == 'want_to_read':
            self.want_to_read.add(book)
        elif shelf_type == 'currently_reading':
            self.currently_reading.add(book)
        elif shelf_type == 'read':
            self.read.add(book)

        # Sync with BookList
        book_list_entry, created = BookList.objects.get_or_create(
            user_profile=self,
            book_item=book,
            defaults={'list_type': shelf_type, 'added_at': timezone.now()}
        )
        if not created:
            book_list_entry.list_type = shelf_type
            book_list_entry.last_accessed = timezone.now()
            book_list_entry.save()

    def remove_from_shelf(self, book, shelf_type):
        """
        Removes a book from a specified shelf (want_to_read, currently_reading, read)
        and deletes the corresponding BookList entry.
        """
        if shelf_type == 'want_to_read':
            self.want_to_read.remove(book)
        elif shelf_type == 'currently_reading':
            self.currently_reading.remove(book)
        elif shelf_type == 'read':
            self.read.remove(book)

        # Optionally delete the BookList entry for this shelf
        BookList.objects.filter(user_profile=self, book_item=book, list_type=shelf_type).delete()

    """# Add helper functions for adding/removing books
    def add_to_want_to_read(self, book_id):
        if book_id not in self.want_to_read:
            self.want_to_read.append(book_id)
            self.save()

    def add_to_currently_reading(self, book_id):
        if book_id not in self.currently_reading:
            self.currently_reading.append(book_id)
            self.save()

    def add_to_read(self, book_id):
        if book_id not in self.read:
            self.read.append(book_id)
            self.save()

    def remove_from_want_to_read(self, book_id):
        if book_id in self.want_to_read:
            self.want_to_read.remove(book_id)
            self.save()

    def remove_from_currently_reading(self, book_id):
        if book_id in self.currently_reading:
            self.currently_reading.remove(book_id)
            self.save()

    def remove_from_read(self, book_id):
        if book_id in self.read:
            self.read.remove(book_id)
            self.save()"""

class BookList(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    book_item = models.ForeignKey(Book, on_delete=models.CASCADE)
    list_type = models.CharField(max_length=20, choices=[('want_to_read', 'Want to Read'), ('currently_reading', 'Currently Reading'), ('read', 'Read')])
    added_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    progress = models.FloatField(default=0)
    pages_read = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.book_item.title} - {self.list_type} - {self.progress}%"
    

class Shelf(models.Model):
    CATEGORY_CHOICES = [
        ('to_read', 'Want to Read'),
        ('currently_reading', 'Currently Reading'),
        ('read', 'Read'),
        ('custom', 'Custom')
    ]
    
    name = models.CharField(max_length=100, unique=False)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='custom')
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    books = models.ManyToManyField(Book, related_name="shelves")
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Friend_Request(models.Model):
    from_user = models.ForeignKey(UserProfile, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(UserProfile, related_name='to_user', on_delete=models.CASCADE)

class Message(models.Model):
    sender = models.ForeignKey(UserProfile, related_name='sent_messages', on_delete=models.CASCADE )
    recipient  = models.ForeignKey(UserProfile, related_name='recieve_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"From {self.sender.user.username} to {self.recipient.user.username} at {self.timestamp}"