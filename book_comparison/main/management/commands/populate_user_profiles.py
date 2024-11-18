# management/commands/populate_user_profiles.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import UserProfile

class Command(BaseCommand):
    help = 'Create UserProfiles for existing users without one'

    def handle(self, *args, **kwargs):
        for user in User.objects.all():
            if not hasattr(user, 'userprofile'):
                UserProfile.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(f'Created UserProfile for {user.username}.'))
            else:
                self.stdout.write(self.style.WARNING(f'UserProfile already exists for {user.username}.'))