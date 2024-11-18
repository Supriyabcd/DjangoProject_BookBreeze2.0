from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import Shelf, UserProfile  

class Command(BaseCommand):
    help = 'Populate shelves for existing users based on their reading preferences'

    def handle(self, *args, **kwargs):
        for user in User.objects.all():
            try:
                user_profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'UserProfile not found for user: {user.username}. Skipping.'))
                continue  # Skip this user if UserProfile does not exist

            # Create shelves based on UserProfile
            if user_profile.want_to_read.exists():
                shelf, created = Shelf.objects.get_or_create(user_profile=user_profile, category='to_read', defaults={'name': 'Want to Read'})
                shelf.books.add(*user_profile.want_to_read.all())
            
            if user_profile.currently_reading.exists():
                shelf, created = Shelf.objects.get_or_create(user_profile=user_profile, category='currently_reading', defaults={'name': 'Currently Reading'})
                shelf.books.add(*user_profile.currently_reading.all())

            if user_profile.read.exists():
                shelf, created = Shelf.objects.get_or_create(user_profile=user_profile, category='read', defaults={'name': 'Read'})
                shelf.books.add(*user_profile.read.all())

        self.stdout.write(self.style.SUCCESS('Shelves populated successfully.'))