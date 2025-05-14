from django.core.management.base import BaseCommand
from api.models import Restaurant, MenuItem, Order, OrderItem
from django.contrib.auth.models import User
from django.utils import timezone
from random import randint

class Command(BaseCommand):
    help = 'Létrehoz néhány teszt adatot az adatbázisban'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Teszt adatok létrehozása...'))

        # Felhasználó létrehozása (ha még nincs)
        # test_user, created = User.objects.get_or_create(username='testuser')
        # if created:
        #     test_user.set_password('secret')
        #     test_user.save()

        # Éttermek létrehozása
        restaurant1 = Restaurant.objects.create(name='Teszt Étterem 1', address='Teszt Cím 1')
        restaurant2 = Restaurant.objects.create(name='Teszt Étterem 2', address='Teszt Cím 2')

        # Menüpontok létrehozása az első étteremhez
        menu_item1_1 = MenuItem.objects.create(restaurant=restaurant1, name='Pizza Margherita', price=12.50)
        menu_item1_2 = MenuItem.objects.create(restaurant=restaurant1, name='Hamburger', price=8.99)
        menu_item1_3 = MenuItem.objects.create(restaurant=restaurant1, name='Saláta', price=6.75)

        # Menüpontok létrehozása a második étteremhez
        menu_item2_1 = MenuItem.objects.create(restaurant=restaurant2, name='Sushi Válogatás', price=19.99)
        menu_item2_2 = MenuItem.objects.create(restaurant=restaurant2, name='Ramen', price=14.50)

        # Rendelés létrehozása az első étteremből a teszt felhasználónak
        order1 = Order.objects.create(customer=test_user, restaurant=restaurant1)
        OrderItem.objects.create(order=order1, menu_item=menu_item1_1, quantity=1, price=menu_item1_1.price)
        OrderItem.objects.create(order=order1, menu_item=menu_item1_2, quantity=1, price=menu_item1_2.price)
        OrderItem.objects.create(order=order1, menu_item=menu_item1_3, quantity=1, price=menu_item1_3.price)

        self.stdout.write(self.style.SUCCESS('Teszt adatok sikeresen létrehozva!'))