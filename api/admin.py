from django.contrib import admin
from .models import Restaurant, MenuItem, Order, OrderItem

# Register the Restaurant model with the admin interface
admin.site.register(Restaurant)

# Register the MenuItem model with the admin interface
admin.site.register(MenuItem)

# Register the Order model with the admin interface
admin.site.register(Order)

# Register the OrderItem model with the admin interface
admin.site.register(OrderItem)