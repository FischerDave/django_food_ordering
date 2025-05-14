from django.db import models
from django.contrib.auth.models import User

class Restaurant(models.Model):
    """
    Represents a restaurant in the system.
    """
    name = models.CharField(max_length=255)
    address = models.TextField()

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    """
    Represents an item on a restaurant's menu.
    """
    restaurant = models.ForeignKey(Restaurant, related_name='menu', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"

class Order(models.Model):
    """
    Represents a customer's order.
    """
    customer = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('received', 'Received'),
            ('preparing', 'Preparing'),
            ('ready', 'Ready'),
            ('delivered', 'Delivered'),
        ],
        default='received'
    )

    def __str__(self):
        return f"Order #{self.id} by {self.customer.username} at {self.restaurant.name}"

class OrderItem(models.Model):
    """
    Represents a specific item within an order.
    """
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    special_instructions = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name} in Order #{self.order.id}"