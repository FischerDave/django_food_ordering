from django.core.management.base import BaseCommand
from api.models import Restaurant, MenuItem, Order, OrderItem
from django.contrib.auth.models import User
from django.utils import timezone
from random import randint

class Command(BaseCommand):
    help = 'Creates some test data in the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating test data...'))

        # Create a test user if they don't exist
        test_user, created = User.objects.get_or_create(username='testuser')
        if created:
            test_user.set_password('$ecret123')
            test_user.save()

        # Create restaurants
        restaurant1 = Restaurant.objects.create(name='Teszt Étterem 1', address='Teszt Cím 1')
        restaurant2 = Restaurant.objects.create(name='Teszt Étterem 2', address='Teszt Cím 2')

        # Create menu items for the first restaurant
        menu_item1_1 = MenuItem.objects.create(restaurant=restaurant1, name='Pizza Margherita', price=12.50)
        menu_item1_2 = MenuItem.objects.create(restaurant=restaurant1, name='Hamburger', price=8.99)
        menu_item1_3 = MenuItem.objects.create(restaurant=restaurant1, name='Saláta', price=6.75)

        # Create menu items for the second restaurant
        menu_item2_1 = MenuItem.objects.create(restaurant=restaurant2, name='Sushi Válogatás', price=19.99)
        menu_item2_2 = MenuItem.objects.create(restaurant=restaurant2, name='Ramen', price=14.50)

        # Create an order for the test user from the first restaurant
        order1 = Order.objects.create(customer=test_user, restaurant=restaurant1)
        OrderItem.objects.create(order=order1, menu_item=menu_item1_1, quantity=1, price=menu_item1_1.price)
        OrderItem.objects.create(order=order1, menu_item=menu_item1_2, quantity=1, price=menu_item1_2.price)
        OrderItem.objects.create(order=order1, menu_item=menu_item1_3, quantity=1, price=menu_item1_3.price)

        self.stdout.write(self.style.SUCCESS('Test data successfully created!'))