from django.urls import path
from . import views

urlpatterns = [
    # Auth endpoints
    path('auth/register/', views.RegistrationView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/who-am-i/', views.WhoAmIView.as_view(), name='who-am-i'),

    # Restaurant endpoints
    path('restaurants/', views.RestaurantListView.as_view(), name='restaurant-list'),
    path('restaurants/<int:pk>/', views.RestaurantDetailView.as_view(), name='restaurant-detail'),
    path('restaurants/<int:id>/menu/', views.RestaurantMenuView.as_view(), name='restaurant-menu'),

    # Order endpoints (customer)
    path('orders/', views.CreateOrderView.as_view(), name='create-order'),
    path('orders/<int:pk>/', views.CustomerOrderDetailView.as_view(), name='customer-order-detail'),

    # Order endpoints (restaurant - assuming users are associated with restaurants)
    path('restaurants/orders/', views.OrderListView.as_view(), name='restaurant-order-list'),
    path('restaurants/orders/<int:pk>/', views.OrderDetailView.as_view(), name='restaurant-order-detail'),
    path('restaurants/orders/<int:pk>/update/', views.UpdateOrderStatusView.as_view(), name='update-order-status'),
]