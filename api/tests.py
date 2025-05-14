from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from .models import Restaurant, MenuItem
from .serializers import RestaurantSerializer, RestaurantDetailSerializer, OrderItem, Order
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class ViewTests(TestCase):
    """
    Tests for basic view functionality (without authentication).
    """
    def setUp(self):
        """
        Sets up the test environment by creating test restaurants and an API client.
        """
        self.client = APIClient()
        self.restaurant1 = Restaurant.objects.create(name="Étterem 1", address="Cím 1")
        self.restaurant2 = Restaurant.objects.create(name="Étterem 2", address="Cím 2")

    def test_restaurant_list_view(self):
        """
        Tests the view for listing all restaurants.
        It checks if the response status code is 200 OK and if the returned data
        matches the serialized list of all restaurants.
        """
        response = self.client.get(reverse('restaurant-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        restaurants = Restaurant.objects.all()
        serializer = RestaurantSerializer(restaurants, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_restaurant_detail_view(self):
        """
        Tests the view for retrieving details of a specific restaurant.
        It checks if the response status code is 200 OK and if the returned data
        matches the serialized details of the requested restaurant.
        """
        response = self.client.get(reverse('restaurant-detail', args=[self.restaurant1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = RestaurantDetailSerializer(self.restaurant1)
        self.assertEqual(response.data, serializer.data)

    def test_restaurant_detail_view_not_found(self):
        """
        Tests the scenario where the requested restaurant detail does not exist.
        It checks if the response status code is 404 Not Found for a non-existent restaurant ID.
        """
        response = self.client.get(reverse('restaurant-detail', args=[999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class AuthEndToEndTests(TestCase):
    """
    End-to-end tests for authentication-related views.
    """
    def setUp(self):
        """
        Sets up the test environment for authentication tests, including creating
        an API client and sample registration and login data.
        """
        self.client = APIClient()
        self.registration_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword',
            'password2': 'testpassword'
        }
        self.login_data = {
            'username': 'testuser',
            'password': 'testpassword'
        }

    def test_user_registration(self):
        """
        Tests the user registration endpoint.
        It checks if the response status code is 201 Created, if a token is returned,
        and if a new user is created in the database.
        """
        response = self.client.post(reverse('register'), self.registration_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_user_login(self):
        """
        Tests the user login endpoint.
        It creates a test user, retrieves their token, and then attempts to log in.
        It checks if the response status code is 200 OK and if a token is returned upon successful login.
        """
        user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        token, created = Token.objects.get_or_create(user=user)
        response = self.client.post(reverse('login'), self.login_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_login_with_invalid_credentials(self):
        """
        Tests the login endpoint with incorrect credentials.
        It checks if the response status code is 401 Unauthorized and if an error message is returned.
        """
        response = self.client.post(reverse('login'), {'username': 'wronguser', 'password': 'wrongpassword'}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_who_am_i_authenticated(self):
        """
        Tests the 'who-am-i' endpoint for an authenticated user.
        It creates a user, gets their token, authenticates the client with the token,
        and then checks if the response returns the correct user information.
        """
        user = User.objects.create_user(username='authuser', password='authpassword', email='auth@example.com')
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(reverse('who-am-i'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'authuser')

    def test_who_am_i_unauthenticated(self):
        """
        Tests the 'who-am-i' endpoint for an unauthenticated user.
        It checks if the response status code is 401 Unauthorized.
        """
        response = self.client.get(reverse('who-am-i'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class RestaurantEndToEndTests(TestCase):
    """
    End-to-end tests for the restaurant-related views.
    """
    def setUp(self):
        """
        Sets up the test environment for restaurant tests, including creating
        test restaurants, menu items, and an API client.
        """
        self.client = APIClient()
        self.restaurant1 = Restaurant.objects.create(name="Teszt Étterem 1", address="Teszt Cím 1")
        self.restaurant2 = Restaurant.objects.create(name="Teszt Étterem 2", address="Teszt Cím 2")
        MenuItem.objects.create(restaurant=self.restaurant1, name="Étel A", price=10)
        MenuItem.objects.create(restaurant=self.restaurant1, name="Étel B", price=15)

    def test_get_restaurant_list(self):
        """
        Tests the endpoint for retrieving a list of all restaurants.
        It checks if the response status code is 200 OK and if the returned list
        contains the expected number and names of restaurants.
        """
        response = self.client.get(reverse('restaurant-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], "Teszt Étterem 1")
        self.assertEqual(response.data[1]['name'], "Teszt Étterem 2")

    def test_get_restaurant_detail(self):
        """
        Tests the endpoint for retrieving details of a specific restaurant, including its menu.
        It checks if the response status code is 200 OK and if the returned data
        contains the expected restaurant name and menu items.
        """
        response = self.client.get(reverse('restaurant-detail', args=[self.restaurant1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Teszt Étterem 1")
        self.assertIn('menu', response.data)
        self.assertEqual(len(response.data['menu']), 2)
        self.assertEqual(response.data['menu'][0]['name'], "Étel A")
        self.assertEqual(float(response.data['menu'][0]['price']), 10.0)

    def test_get_restaurant_menu(self):
        """
        Tests the endpoint for retrieving the menu of a specific restaurant.
        It checks if the response status code is 200 OK and if the returned list
        contains the expected menu items.
        """
        response = self.client.get(reverse('restaurant-menu', args=[self.restaurant1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], "Étel A")
        self.assertEqual(response.data[1]['name'], "Étel B")

    def test_get_restaurant_not_found(self):
        """
        Tests the scenario where the requested restaurant detail does not exist
        when accessing the detail endpoint.
        It checks if the response status code is 404 Not Found for a non-existent restaurant ID.
        """
        response = self.client.get(reverse('restaurant-detail', args=[999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_restaurant_menu_not_found(self):
        """
        Tests the scenario where the requested restaurant menu does not exist
        when accessing the menu endpoint.
        It checks if the response status code is 404 Not Found for a non-existent restaurant ID.
        """
        response = self.client.get(reverse('restaurant-menu', args=[999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class OrderEndToEndTests(TestCase):
    """
    End-to-end tests for the order creation endpoint.
    """
    def setUp(self):
        """
        Sets up the test environment for order tests, including creating
        an API client, a test user with a token, a restaurant, and menu items.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(username='orderuser', password='orderpassword')
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.restaurant = Restaurant.objects.create(name="Rendelő Étterem", address="Rendelő Cím")
        self.item1 = MenuItem.objects.create(restaurant=self.restaurant, name="Pizza", price=20)
        self.item2 = MenuItem.objects.create(restaurant=self.restaurant, name="Burger", price=15)
        self.order_data = {
            'restaurantId': self.restaurant.id,
            'items': [
                {'menuItemId': self.item1.id, 'quantity': 1},
                {'menuItemId': self.item2.id, 'quantity': 2, 'special_instructions': 'Extra feltét'}
            ]
        }

    def test_create_order(self):
        """
        Tests the creation of a new order.
        It checks if the response status code is 201 Created and if the returned
        order data contains the expected information, including items, customer, and restaurant.
        """
        response = self.client.post(reverse('create-order'), self.order_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(len(response.data['items']), 2)
        self.assertEqual(response.data['items'][0]['menu_item']['name'], "Pizza")
        self.assertEqual(response.data['items'][1]['quantity'], 2)
        self.assertEqual(response.data['customer']['username'], 'orderuser')
        self.assertEqual(response.data['restaurant']['name'], "Rendelő Étterem")

    def test_create_order_invalid_restaurant(self):
        """
        Tests the creation of an order with an invalid restaurant ID.
        It checks if the response status code is 400 Bad Request and if the
        error message indicates an invalid restaurant ID.
        """
        invalid_data = self.order_data.copy()
        invalid_data['restaurantId'] = 999
        response = self.client.post(reverse('create-order'), invalid_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('restaurantId', response.data)

    def test_create_order_invalid_menu_item(self):
        """
        Tests the creation of an order with an invalid menu item ID.
        It checks if the response status code is 400 Bad Request and if the
        error message indicates an invalid menu item ID.
        """
        invalid_data = self.order_data.copy()
        invalid_data['items'][0]['menuItemId'] = 999
        response = self.client.post(reverse('create-order'), invalid_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('items', response.data)

class CustomerOrderEndToEndTests(TestCase):
    """
    End-to-end tests for retrieving customer-specific order details.
    """
    def setUp(self):
        """
        Sets up the test environment for customer order tests, including creating
        API clients for two different customers, restaurants, menu items, and orders.
        """
        self.client = APIClient()
        # Create two test users (customers)
        self.customer1 = User.objects.create_user(username='customer1', password='password1')
        self.customer2 = User.objects.create_user(username='customer2', password='password2')
        # Create a test restaurant
        self.restaurant = Restaurant.objects.create(name="Teszt Étterem", address="Teszt Cím")
        # Create a test menu item
        self.item1 = MenuItem.objects.create(restaurant=self.restaurant, name="Étel 1", price=10)
        # Create an order for customer1
        self.order1_customer1 = Order.objects.create(customer=self.customer1, restaurant=self.restaurant)
        OrderItem.objects.create(order=self.order1_customer1, menu_item=self.item1, quantity=1)
        # Create an order for customer2
        self.order2_customer2 = Order.objects.create(customer=self.customer2, restaurant=self.restaurant)
        OrderItem.objects.create(order=self.order2_customer2, menu_item=self.item1, quantity=1)

        # Create an authenticated API client for customer1
        self.client_customer1 = APIClient()
        token_customer1, _ = Token.objects.get_or_create(user=self.customer1)
        self.client_customer1.credentials(HTTP_AUTHORIZATION='Token ' + token_customer1.key)

        # Create an authenticated API client for customer2
        self.client_customer2 = APIClient()
        token_customer2, _ = Token.objects.get_or_create(user=self.customer2)
        self.client_customer2.credentials(HTTP_AUTHORIZATION='Token ' + token_customer2.key)

    def test_customer_can_retrieve_own_order_detail(self):
        """
        Tests that an authenticated customer can retrieve the details of their own order.
        It checks if the response status code is 200 OK and if the returned
        order ID and customer username match the expected values.
        """
        response = self.client_customer1.get(reverse('customer-order-detail', args=[self.order1_customer1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order1_customer1.id)
        self.assertEqual(response.data['customer']['username'], 'customer1')

    def test_customer_cannot_retrieve_other_customer_order_detail(self):
        """
        Tests that an authenticated customer cannot retrieve the details of another customer's order.
        It checks if the response status code is 404 Not Found when trying to access someone else's order.
        """
        response = self.client_customer1.get(reverse('customer-order-detail', args=[self.order2_customer2.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_user_cannot_retrieve_order_detail(self):
        """
        Tests that an unauthenticated user cannot retrieve any order details.
        It checks if the response status code is 401 Unauthorized.
        """
        client = APIClient()
        response = client.get(reverse('customer-order-detail', args=[self.order1_customer1.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)