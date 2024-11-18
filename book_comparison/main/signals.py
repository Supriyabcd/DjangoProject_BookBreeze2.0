import logging
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from .models import UserProfile, Shelf, BookList, Book

logger = logging.getLogger(__name__)

# Signal to create a UserProfile and default shelves for each new user
@receiver(post_save, sender=User)
def create_user_profile_and_default_shelves(sender, instance, created, **kwargs):
    if created:
        # Create UserProfile
        user_profile = UserProfile.objects.create(user=instance)

        # Create default shelves for each user
        Shelf.objects.create(user_profile=user_profile, name='Want to Read', category='to_read', is_default=True)
        Shelf.objects.create(user_profile=user_profile, name='Currently Reading', category='currently_reading', is_default=True)
        Shelf.objects.create(user_profile=user_profile, name='Read', category='read', is_default=True)
        logger.info(f'Default shelves created for {instance}')

# Signal to sync UserProfile's want_to_read with Shelf and BookList
@receiver(m2m_changed, sender=UserProfile.want_to_read.through)
def sync_want_to_read_with_shelves_and_booklist(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for book_id in pk_set:
            book = Book.objects.get(pk=book_id)
            # Add book to the "Want to Read" Shelf
            want_to_read_shelf, created = Shelf.objects.get_or_create(
                user_profile=instance,
                category='to_read',
                defaults={'name': 'Want to Read'}
            )
            want_to_read_shelf.books.add(book)

            # Create or update the corresponding BookList entry
            BookList.objects.get_or_create(
                user_profile=instance,
                book_item=book,
                defaults={'list_type': 'want_to_read', 'added_at': timezone.now(), 'last_accessed': timezone.now()}
            )
            logger.info(f' synced want_to_read with Shelf and BookList for {instance}')

    elif action == "post_remove":
        for book_id in pk_set:
            book = Book.objects.get(pk=book_id)
            # Remove the book from the "Want to Read" Shelf
            want_to_read_shelf = Shelf.objects.filter(user_profile=instance, category='to_read').first()
            if want_to_read_shelf:
                want_to_read_shelf.books.remove(book)

            # Remove the BookList entry for this book with 'want_to_read' status
            BookList.objects.filter(user_profile=instance, book_item=book, list_type='want_to_read').delete()

# Signal to sync UserProfile's currently_reading with Shelf and BookList
@receiver(m2m_changed, sender=UserProfile.currently_reading.through)
def sync_currently_reading_with_shelves_and_booklist(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for book_id in pk_set:
            book = Book.objects.get(pk=book_id)
            # Add book to the "Currently Reading" Shelf
            currently_reading_shelf, created = Shelf.objects.get_or_create(
                user_profile=instance,
                category='currently_reading',
                defaults={'name': 'Currently Reading'}
            )
            currently_reading_shelf.books.add(book)

            # Create or update the corresponding BookList entry
            BookList.objects.get_or_create(
                user_profile=instance,
                book_item=book,
                defaults={'list_type': 'currently_reading', 'added_at': timezone.now(), 'last_accessed': timezone.now()}
            )
            logger.info(f' synced currently_reading with Shelf and BookList for {instance}')

    elif action == "post_remove":
        for book_id in pk_set:
            book = Book.objects.get(pk=book_id)
            # Remove the book from the "Currently Reading" Shelf
            currently_reading_shelf = Shelf.objects.filter(user_profile=instance, category='currently_reading').first()
            if currently_reading_shelf:
                currently_reading_shelf.books.remove(book)

            # Remove the BookList entry for this book with 'currently_reading' status
            BookList.objects.filter(user_profile=instance, book_item=book, list_type='currently_reading').delete()

# Signal to sync UserProfile's read with Shelf and BookList
@receiver(m2m_changed, sender=UserProfile.read.through)
def sync_read_with_shelves_and_booklist(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for book_id in pk_set:
            book = Book.objects.get(pk=book_id)
            # Add book to the "Read" Shelf
            read_shelf, created = Shelf.objects.get_or_create(
                user_profile=instance,
                category='read',
                defaults={'name': 'Read'}
            )
            read_shelf.books.add(book)

            # Create or update the corresponding BookList entry
            BookList.objects.get_or_create(
                user_profile=instance,
                book_item=book,
                defaults={'list_type': 'read', 'added_at': timezone.now(), 'last_accessed': timezone.now()}
            )
            logger.info(f' synced read with Shelf and BookList for {instance}')

    elif action == "post_remove":
        for book_id in pk_set:
            book = Book.objects.get(pk=book_id)
            # Remove the book from the "Read" Shelf
            read_shelf = Shelf.objects.filter(user_profile=instance, category='read').first()
            if read_shelf:
                read_shelf.books.remove(book)

            # Remove the BookList entry for this book with 'read' status
            BookList.objects.filter(user_profile=instance, book_item=book, list_type='read').delete()
