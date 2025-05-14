from rest_framework import serializers
from .models import Restaurant, MenuItem, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class RestaurantSerializer(serializers.ModelSerializer):
    """
    Serializer for the Restaurant model.
    """
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address']

class MenuItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the MenuItem model.
    """
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price']

class RestaurantDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying detailed information about a Restaurant, including its menu.
    """
    menu = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'menu']

    def get_menu(self, instance):
        """
        Custom method to retrieve and serialize the menu items for a restaurant.
        """
        menu_items = MenuItem.objects.filter(restaurant=instance)
        return MenuItemSerializer(menu_items, many=True).data


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model (Django's built-in User model).
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the OrderItem model.
    """
    menu_item = MenuItemSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'quantity', 'special_instructions']

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model, including related customer, restaurant, and items.
    """
    customer = UserSerializer(read_only=True)
    restaurant = RestaurantSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'customer', 'restaurant', 'created_at', 'status', 'items']

class OrderItemCreateSerializer(serializers.Serializer):
    """
    Serializer for creating OrderItem objects when placing a new order.
    """
    menuItemId = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(min_value=1, required=True)
    special_instructions = serializers.CharField(allow_blank=True, required=False)

class CreateOrderSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new Order, including handling the creation of related OrderItem objects.
    """
    items = OrderItemCreateSerializer(many=True, write_only=True)
    restaurantId = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'restaurantId', 'items', 'customer']
        read_only_fields = ['id', 'customer']

    def create(self, validated_data):
        """
        Overrides the create method to handle the creation of the Order and its associated OrderItems.
        """
        restaurant_id = validated_data.pop('restaurantId')
        items_data = validated_data.pop('items')
        customer = validated_data.pop('customer')

        try:
            restaurant = Restaurant.objects.get(pk=restaurant_id)
        except Restaurant.DoesNotExist:
            raise serializers.ValidationError({'restaurantId': 'Invalid restaurant ID.'})

        order = Order.objects.create(customer=customer, restaurant=restaurant)

        order_items = []
        for item_data in items_data:
            try:
                menu_item = MenuItem.objects.get(pk=item_data['menuItemId'], restaurant=restaurant)
            except MenuItem.DoesNotExist:
                raise serializers.ValidationError({'items': f"Invalid menu item ID: {item_data['menuItemId']} for the given restaurant."})
            order_item = OrderItem.objects.create(order=order, menu_item=menu_item, quantity=item_data['quantity'], special_instructions=item_data.get('special_instructions', ''))
            order_items.append(order_item)

        return order

    def to_representation(self, instance):
        """
        Overrides the to_representation method to customize the output format of the Order.
        """
        representation = super().to_representation(instance)
        representation['items'] = OrderItemSerializer(instance.items.all(), many=True).data
        representation['customer'] = {'id': instance.customer.id, 'username': instance.customer.username}
        representation['restaurant'] = {'id': instance.restaurant.id, 'name': instance.restaurant.name}
        return representation

class RegistrationSerializer(serializers.Serializer):
    """
    Serializer for user registration.
    """
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        """
        Custom validation to ensure passwords match and the username/email are unique.
        """
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "This username is already taken."})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "This email address is already registered."})
        return data

    def create(self, validated_data):
        """
        Overrides the create method to create a new User.
        """
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)