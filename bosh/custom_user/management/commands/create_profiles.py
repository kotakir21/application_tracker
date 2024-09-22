# custom_user/management/commands/create_profiles.py

from django.core.management.base import BaseCommand
from custom_user.models import User, Profile

class Command(BaseCommand):
    help = 'Create missing profiles for users'

    def handle(self, *args, **kwargs):
        users_without_profiles = User.objects.filter(profile__isnull=True)
        for user in users_without_profiles:
            Profile.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Profile created for user {user.email}'))
