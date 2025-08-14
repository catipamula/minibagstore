from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, CartItem, Order, OrderItem
from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

# For user registration and info
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image', 'stock', 'category']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = CartItem
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = '__all__'
