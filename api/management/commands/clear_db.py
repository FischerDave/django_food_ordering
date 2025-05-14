from django.core.management.base import BaseCommand
from api.models import Restaurant, MenuItem, Order, OrderItem
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Deletes all test data from the database'

    def handle(self, *args, **options):
        # Delete all restaurants
        Restaurant.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All restaurants deleted.'))

        # Delete all menu items
        MenuItem.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All menu items deleted.'))

        # Delete all orders
        Order.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All orders deleted.'))

        # Delete all order items
        OrderItem.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All order items deleted.'))

        # Attempt to delete the test user
        try:
            test_user = User.objects.get(username='testuser')
            test_user.delete()
            self.stdout.write(self.style.SUCCESS('Test user deleted.'))
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('Test user does not exist.'))

        self.stdout.write(self.style.SUCCESS('Test data successfully deleted!'))