"""
Django management command to create a superuser if one doesn't exist.
Uses environment variables for credentials.
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError
from decouple import config


class Command(BaseCommand):
    help = 'Create a superuser if one does not exist'

    def handle(self, *args, **options):
        """Create superuser from environment variables if none exists"""
        
        # Get credentials from environment variables with better defaults
        username = config('DJANGO_SUPERUSER_USERNAME', default='admin')
        email = config('DJANGO_SUPERUSER_EMAIL', default='admin@example.com')
        password = config('DJANGO_SUPERUSER_PASSWORD', default='admin123')

        self.stdout.write(f'Attempting to create superuser: {username}')
        
        # Check if this specific user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User {username} already exists. Skipping creation.')
            )
            return

        # Check if any superuser already exists
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING('A superuser already exists. Skipping creation.')
            )
            return

        try:
            # Create the superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created superuser: {username} with email: {email}'
                )
            )
            
            # Verify the user was created correctly
            if user.is_superuser and user.is_staff:
                self.stdout.write(
                    self.style.SUCCESS('✓ Superuser privileges confirmed')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('✗ Superuser privileges not set correctly')
                )
            
        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'IntegrityError creating superuser: {str(e)}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {str(e)}')
            ) 
        pass 