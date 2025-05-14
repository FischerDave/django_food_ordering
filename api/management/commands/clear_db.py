from django.core.management.base import BaseCommand
from api.models import Restaurant, MenuItem, Order, OrderItem
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Törli az összes teszt adatot az adatbázisból'

    def handle(self, *args, **options):
        Restaurant.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Összes étterem törölve.'))

        MenuItem.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Összes menüpont törölve.'))

        Order.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Összes rendelés törölve.'))

        OrderItem.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Összes rendelési tétel törölve.'))

        try:
            test_user = User.objects.get(username='testuser')
            test_user.delete()
            self.stdout.write(self.style.SUCCESS('Teszt felhasználó törölve.'))
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('Teszt felhasználó nem létezik.'))

        self.stdout.write(self.style.SUCCESS('Teszt adatok sikeresen törölve!'))