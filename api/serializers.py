from rest_framework import serializers
from .models import Restaurant, MenuItem, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address']

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price']

class RestaurantDetailSerializer(serializers.ModelSerializer):
    menu = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'menu']

    def get_menu(self, instance):
        menu_items = MenuItem.objects.filter(restaurant=instance)
        return MenuItemSerializer(menu_items, many=True).data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'quantity', 'special_instructions']

class OrderSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    restaurant = RestaurantSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'customer', 'restaurant', 'created_at', 'status', 'items']

class OrderItemCreateSerializer(serializers.Serializer):
    menuItemId = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(min_value=1, required=True)
    special_instructions = serializers.CharField(allow_blank=True, required=False)

class CreateOrderSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)
    restaurantId = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'restaurantId', 'items', 'customer']
        read_only_fields = ['id', 'customer']

    def create(self, validated_data):
        restaurant_id = validated_data.pop('restaurantId')
        items_data = validated_data.pop('items')
        customer = validated_data.pop('customer')

        try:
            restaurant = Restaurant.objects.get(pk=restaurant_id)
        except Restaurant.DoesNotExist:
            raise serializers.ValidationError({'restaurantId': 'Érvénytelen étterem ID.'})

        order = Order.objects.create(customer=customer, restaurant=restaurant)

        order_items = []
        for item_data in items_data:
            try:
                menu_item = MenuItem.objects.get(pk=item_data['menuItemId'], restaurant=restaurant)
            except MenuItem.DoesNotExist:
                raise serializers.ValidationError({'items': f"Érvénytelen menüpont ID: {item_data['menuItemId']} az adott étteremben."})
            order_item = OrderItem.objects.create(order=order, menu_item=menu_item, quantity=item_data['quantity'], special_instructions=item_data.get('special_instructions', ''))
            order_items.append(order_item)

        return order

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['items'] = OrderItemSerializer(instance.items.all(), many=True).data
        representation['customer'] = {'id': instance.customer.id, 'username': instance.customer.username}
        representation['restaurant'] = {'id': instance.restaurant.id, 'name': instance.restaurant.name}
        return representation

class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "A jelszavak nem egyeznek."})
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Ez a felhasználónév már foglalt."})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Ez az e-mail cím már regisztrálva van."})
        return data

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)