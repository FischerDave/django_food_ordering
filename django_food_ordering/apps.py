from django.apps import AppConfig

class DjangoFoodOrderingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_food_ordering'

    def ready(self):
        import django_food_ordering.signals