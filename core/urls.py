from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('start_order/', views.start_order_view, name='start_order'),
    path('order/', views.select_meals_view, name='select_meals'),
    path('cart/', views.cart_view, name='cart'),
    path('confirm_order/', views.confirm_order_view, name='confirm_order'),
    path('order_success/<int:order_id>/', views.order_success_view, name='order_success'),
    path('customize_meal/<int:meal_id>/', views.customize_meal_view, name='customize_meal'),
    path('select_meal/', views.select_meals_view, name='select_meal'),

    path('users/', views.user_list_view, name='user_list'),  # List of users
    path('user/<int:user_id>/orders/', views.user_orders_view, name='user_orders'),
]
