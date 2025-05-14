from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .serializers import (
    RegistrationSerializer, LoginSerializer, UserSerializer,
    RestaurantSerializer, RestaurantDetailSerializer, MenuItemSerializer,
    OrderSerializer, OrderItemSerializer, CreateOrderSerializer
)

from rest_framework.decorators import api_view

from .models import Order, OrderItem, Restaurant, MenuItem

class RegistrationView(generics.GenericAPIView):
    """
    API endpoint for user registration.
    Allows any user to create a new account.
    """
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Handles the POST request for user registration.
        Validates the registration data and creates a new user.
        Upon successful registration, it generates and returns an authentication token.
        Returns a 400 Bad Request if the registration data is invalid.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(generics.GenericAPIView):
    """
    API endpoint for user login.
    Allows any user to log in with their username and password.
    """
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Handles the POST request for user login.
        Authenticates the user based on the provided username and password.
        Upon successful authentication, it generates or retrieves the user's authentication token.
        Returns a 200 OK with the token, a 401 Unauthorized for invalid credentials,
        or a 400 Bad Request for invalid input data.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': token.key}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WhoAmIView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve information about the currently authenticated user.
    Requires user authentication.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        """
        Overrides get_object to return the currently authenticated user.
        """
        return self.request.user

class RestaurantListView(generics.ListAPIView):
    """
    API endpoint to list all restaurants.
    Allows any authenticated user to view the list of restaurants.
    """
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

class RestaurantDetailView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve details of a specific restaurant.
    Allows any authenticated user to view the details of a restaurant.
    """
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantDetailSerializer

@api_view(['GET'])
def restaurant_menu(request, id):
    """
    API endpoint to retrieve the menu of a specific restaurant.
    Allows any authenticated user to view the menu.
    Uses a function-based view with the @api_view decorator.
    """
    try:
        restaurant = Restaurant.objects.get(pk=id)
    except Restaurant.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    menu_items = restaurant.menu.all()
    serializer = MenuItemSerializer(menu_items, many=True)
    return Response(serializer.data)

class OrderListView(generics.ListAPIView):
    """
    API endpoint to list all orders.
    Requires user authentication to view the list of orders.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.all() # Reverted to fetching all orders

class OrderDetailView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve details of a specific order.
    Requires user authentication to view the details of an order.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.all() # Reverted to fetching all orders

class CreateOrderView(generics.CreateAPIView):
    """
    API endpoint to create a new order.
    Requires user authentication to create an order.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateOrderSerializer

    def perform_create(self, serializer):
        """
        Overrides perform_create to automatically associate the authenticated user with the order as the customer.
        """
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=self.request.user)

class UpdateOrderStatusView(generics.UpdateAPIView):
    """
    API endpoint to update the status of a specific order.
    Requires user authentication to update the order status.
    Allows only PATCH requests.
    """
    permission_classes = [permissions.IsAuthenticated] # Authentication is required
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    http_method_names = ['patch']

    def patch(self, request, *args, **kwargs):
        """
        Handles the PATCH request to update the order status.
        Retrieves the order instance, serializes the update data, validates it,
        and saves the new status to the order.
        """
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(status=request.data.get('status'))
        return Response(serializer.data)

class CustomerOrderDetailView(generics.RetrieveAPIView):
    """
    API endpoint for an authenticated customer to retrieve details of their own specific order.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        """
        Overrides get_queryset to only return orders associated with the currently authenticated user.
        """
        return Order.objects.filter(customer=self.request.user)

class RestaurantMenuView(generics.ListAPIView):
    """
    API endpoint to retrieve the menu items for a specific restaurant.
    Allows any authenticated user to view the menu.
    """
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        """
        Overrides get_queryset to retrieve menu items for the specified restaurant ID in the URL.
        Uses get_object_or_404 to handle cases where the restaurant does not exist.
        """
        restaurant_id = self.kwargs.get('id')
        restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
        return restaurant.menu.all()