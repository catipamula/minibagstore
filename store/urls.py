from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token  # <- DRF's token view

urlpatterns = [
    # Products
    path('products/', views.get_products, name='get_products'),
    path('products/<int:pk>/', views.get_product, name='get_product'),

    # Cart
    path('cart/', views.cart, name='cart'),               # GET & POST
    path('cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),  # DELETE

    # Checkout
    path('checkout/', views.checkout, name='checkout'),   # POST

    # Authentication
    path('register/', views.register, name='register'),   # POST
    path('login/', views.login_user, name='login'),       # POST

    # Token Auth (correct)
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),

    # Password reset
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset-confirm/', views.password_reset_confirm, name='password_reset_confirm'),

    path('api/place-order/', views.place_order, name='place_order'),
    path('api/orders/', views.orders_list, name='orders_list'),
]
