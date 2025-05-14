from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from .models import Restaurant, MenuItem
from .serializers import RestaurantSerializer, RestaurantDetailSerializer, OrderItem, Order
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class ViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.restaurant1 = Restaurant.objects.create(name="Étterem 1", address="Cím 1")
        self.restaurant2 = Restaurant.objects.create(name="Étterem 2", address="Cím 2")

    def test_restaurant_list_view(self):
        response = self.client.get(reverse('restaurant-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        restaurants = Restaurant.objects.all()
        serializer = RestaurantSerializer(restaurants, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_restaurant_detail_view(self):
        response = self.client.get(reverse('restaurant-detail', args=[self.restaurant1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = RestaurantDetailSerializer(self.restaurant1)
        self.assertEqual(response.data, serializer.data)

    def test_restaurant_detail_view_not_found(self):
        response = self.client.get(reverse('restaurant-detail', args=[999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class AuthEndToEndTests(TestCase):

    def setUp(self):
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
        response = self.client.post(reverse('register'), self.registration_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        # Itt potenciálisan létrehozhattál tokent rosszul

    def test_user_login(self):
        user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        token, created = Token.objects.get_or_create(user=user)
        response = self.client.post(reverse('login'), self.login_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_login_with_invalid_credentials(self):
        response = self.client.post(reverse('login'), {'username': 'wronguser', 'password': 'wrongpassword'}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_who_am_i_authenticated(self):
        user = User.objects.create_user(username='authuser', password='authpassword', email='auth@example.com')
        token, _ = Token.objects.get_or_create(user=user) # Ez a helyes mód
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(reverse('who-am-i'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'authuser')

    def test_who_am_i_unauthenticated(self):
        response = self.client.get(reverse('who-am-i'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class RestaurantEndToEndTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.restaurant1 = Restaurant.objects.create(name="Teszt Étterem 1", address="Teszt Cím 1")
        self.restaurant2 = Restaurant.objects.create(name="Teszt Étterem 2", address="Teszt Cím 2")
        MenuItem.objects.create(restaurant=self.restaurant1, name="Étel A", price=10)
        MenuItem.objects.create(restaurant=self.restaurant1, name="Étel B", price=15)

    def test_get_restaurant_list(self):
        response = self.client.get(reverse('restaurant-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], "Teszt Étterem 1")
        self.assertEqual(response.data[1]['name'], "Teszt Étterem 2")

    def test_get_restaurant_detail(self):
        response = self.client.get(reverse('restaurant-detail', args=[self.restaurant1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Teszt Étterem 1")
        self.assertIn('menu', response.data)
        self.assertEqual(len(response.data['menu']), 2)
        self.assertEqual(response.data['menu'][0]['name'], "Étel A")
        self.assertEqual(float(response.data['menu'][0]['price']), 10.0)

    def test_get_restaurant_menu(self):
        response = self.client.get(reverse('restaurant-menu', args=[self.restaurant1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], "Étel A")
        self.assertEqual(response.data[1]['name'], "Étel B")

    def test_get_restaurant_not_found(self):
        response = self.client.get(reverse('restaurant-detail', args=[999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_restaurant_menu_not_found(self):
        response = self.client.get(reverse('restaurant-menu', args=[999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class OrderEndToEndTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='orderuser', password='orderpassword')
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.restaurant = Restaurant.objects.create(name="Rendelő Étterem", address="Rendelő Cím")
        self.item1 = MenuItem.objects.create(restaurant=self.restaurant, name="Pizza", price=20)
        self.item2 = MenuItem.objects.create(restaurant=self.restaurant, name="Burger", price=15)
        self.order_data = {
            'restaurantId': self.restaurant.id,
            'order_items_for_create': [
                {'menuItemId': self.item1.id, 'quantity': 1},
                {'menuItemId': self.item2.id, 'quantity': 2, 'special_instructions': 'Extra feltét'}
            ]
        }

    def test_create_order(self):
        response = self.client.post(reverse('create-order'), self.order_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(len(response.data['items']), 2)
        self.assertEqual(response.data['items'][0]['menu_item']['name'], "Pizza")
        self.assertEqual(response.data['items'][1]['quantity'], 2)
        self.assertEqual(response.data['customer']['username'], 'orderuser')
        self.assertEqual(response.data['restaurant']['name'], "Rendelő Étterem")

    def test_create_order_invalid_restaurant(self):
        invalid_data = self.order_data.copy()
        invalid_data['restaurantId'] = 999
        response = self.client.post(reverse('create-order'), invalid_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('restaurantId', response.data)

    def test_create_order_invalid_menu_item(self):
        invalid_data = self.order_data.copy()
        invalid_data['order_items_for_create'][0]['menuItemId'] = 999
        response = self.client.post(reverse('create-order'), invalid_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('order_items_for_create', response.data)

class CustomerOrderEndToEndTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer1 = User.objects.create_user(username='customer1', password='password1')
        self.customer2 = User.objects.create_user(username='customer2', password='password2')
        self.restaurant = Restaurant.objects.create(name="Teszt Étterem", address="Teszt Cím")
        self.item1 = MenuItem.objects.create(restaurant=self.restaurant, name="Étel 1", price=10)
        self.order1_customer1 = Order.objects.create(customer=self.customer1, restaurant=self.restaurant)
        OrderItem.objects.create(order=self.order1_customer1, menu_item=self.item1, quantity=1)
        self.order2_customer2 = Order.objects.create(customer=self.customer2, restaurant=self.restaurant)
        OrderItem.objects.create(order=self.order2_customer2, menu_item=self.item1, quantity=1)

        self.client_customer1 = APIClient()
        token_customer1, _ = Token.objects.get_or_create(user=self.customer1)
        self.client_customer1.credentials(HTTP_AUTHORIZATION='Token ' + token_customer1.key)

        self.client_customer2 = APIClient()
        token_customer2, _ = Token.objects.get_or_create(user=self.customer2)
        self.client_customer2.credentials(HTTP_AUTHORIZATION='Token ' + token_customer2.key)

    def test_customer_can_retrieve_own_order_detail(self):
        response = self.client_customer1.get(reverse('customer-order-detail', args=[self.order1_customer1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order1_customer1.id)
        self.assertEqual(response.data['customer']['username'], 'customer1')

    def test_customer_cannot_retrieve_other_customer_order_detail(self):
        response = self.client_customer1.get(reverse('customer-order-detail', args=[self.order2_customer2.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_user_cannot_retrieve_order_detail(self):
        client = APIClient()
        response = client.get(reverse('customer-order-detail', args=[self.order1_customer1.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)