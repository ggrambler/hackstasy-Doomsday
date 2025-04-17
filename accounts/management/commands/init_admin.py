from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates a superuser if none exists'

    def handle(self, *args, **options):
        if User.objects.count() == 0:
            username = 'admin'
            email = 'admin@example.com'
            password = 'admin123'
            print('Creating superuser account...')
            admin = User.objects.create_superuser(username=username, email=email, password=password)
            admin.save()
        else:
            print('Superuser account already exists.')
