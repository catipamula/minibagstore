from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    CATEGORY_CHOICES = [
        ("Mobile & Accessories", "Mobile & Accessories"),
        ("Computers & Laptops", "Computers & Laptops"),
        ("Audio & Headphones", "Audio & Headphones"),
        ("Smart Home & Wearables", "Smart Home & Wearables"),
        ("Gaming & Entertainment", "Gaming & Entertainment"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="products/")
    stock = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="Mobile & Accessories")

    def __str__(self):
        return self.name



class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # allow null for migration

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Order(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    # Removed JSONField for items because we'll now relate via OrderItem
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=10, default="COD")
    card_details = models.JSONField(null=True, blank=True)


    def __str__(self):
        return f"Order #{self.id} - {self.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="order_items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
