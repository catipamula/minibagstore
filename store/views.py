from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from .models import Product, CartItem, Order, OrderItem
from .serializers import ProductSerializer, CartItemSerializer, OrderSerializer, UserSerializer
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# -------------------------
# User authentication
# -------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not email or not password:
        return Response({'error': 'All fields are required'}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=400)

    user = User.objects.create_user(username=username, email=email, password=password)
    return Response({'message': 'User registered successfully', 'user_id': user.id})

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response({'error': 'Both username and password are required'}, status=400)

    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({'message': 'Login successful', 'token': token.key, 'user_id': user.id})
    return Response({'error': 'Invalid credentials'}, status=401)

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=400)
    try:
        user = User.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        # Normally send email; for testing we just return link
        reset_link = f"http://localhost:3000/reset-password-confirm/{uid}/{token}/"
        print("Reset link:", reset_link)
        return Response({'detail': 'Password reset link sent', 'link': reset_link})
    except User.DoesNotExist:
        return Response({'error': 'User with this email does not exist'}, status=404)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    uidb64 = request.data.get('uid')
    token = request.data.get('token')
    new_password = request.data.get('new_password')

    if not uidb64 or not token or not new_password:
        return Response({'error': 'All fields are required'}, status=400)

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        return Response({'error': 'Invalid UID'}, status=400)

    if default_token_generator.check_token(user, token):
        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Password reset successful'})
    return Response({'error': 'Invalid token'}, status=400)



# -------------------------
# Products
# -------------------------

@api_view(['GET'])
@permission_classes([AllowAny])
def get_products(request):
    category = request.query_params.get('category')
    products = Product.objects.all()
    if category:
        products = products.filter(category=category)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_product(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)


# -------------------------
# Cart
# -------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cart(request):
    user = request.user

    # GET /cart/
    if request.method == 'GET':
        cart_items = CartItem.objects.filter(user=user)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)

    # POST /cart/  --> Add to cart
    elif request.method == 'POST':
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response({'error': 'Product ID is required'}, status=400)

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)

        try:
            quantity = int(quantity)
        except ValueError:
            return Response({'error': 'Quantity must be an integer'}, status=400)

        cart_item, created = CartItem.objects.get_or_create(user=user, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        return Response({'message': 'Product added to cart', 'cart_item_id': cart_item.id})


# DELETE /cart/<id>/
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, pk):
    user = request.user
    try:
        cart_item = CartItem.objects.get(pk=pk, user=user)
        cart_item.delete()
        return Response({'message': 'Removed from cart'})
    except CartItem.DoesNotExist:
        return Response({'error': 'Cart item not found'}, status=404)


# -------------------------
# Checkout
# -------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout(request):
    user = request.user
    name = request.data.get('name')
    email = request.data.get('email')
    address = request.data.get('address')
    payment_number = request.data.get('payment_number', None)

    if not name or not email or not address:
        return Response({'error': 'Name, email, and address are required'}, status=400)

    cart_items = CartItem.objects.filter(user=user)
    if not cart_items.exists():
        return Response({'error': 'Cart is empty'}, status=400)

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    order = Order.objects.create(
        user=user,
        name=name,
        email=email,
        address=address,
        total_price=total_price,
        payment_number=payment_number
    )

    for item in cart_items:
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

    cart_items.delete()

    # Optional: send email
    send_mail(
        'Order Confirmation',
        f'Hi {name}, your order #{order.id} has been placed successfully. Total: ₹{total_price}',
        'noreply@bagstore.com',
        [email],
        fail_silently=True,
    )

    return Response({'message': 'Order placed successfully', 'order_id': order.id})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout(request):
    user = request.user
    name = request.data.get('name')
    email = request.data.get('email')
    address = request.data.get('address')
    payment_method = request.data.get('payment_method')  # "cod" or "credit_card"
    card_number = request.data.get('card_number')  # only if credit_card
    card_expiry = request.data.get('card_expiry')
    card_cvv = request.data.get('card_cvv')

    if not name or not email or not address:
        return Response({'error': 'Name, email, and address are required'}, status=400)

    if not payment_method or payment_method not in ["cod", "credit_card"]:
        return Response({'error': 'Valid payment method is required'}, status=400)

    if payment_method == "credit_card":
        if not card_number or not card_expiry or not card_cvv:
            return Response({'error': 'All credit card details are required'}, status=400)
        # ⚠️ For production, integrate with a secure payment gateway
        if len(str(card_number)) < 12:
            return Response({'error': 'Invalid card number'}, status=400)

    cart_items = CartItem.objects.filter(user=user)
    if not cart_items.exists():
        return Response({'error': 'Cart is empty'}, status=400)

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    order = Order.objects.create(
        user=user,
        name=name,
        email=email,
        address=address,
        total_price=total_price,
        payment_method=payment_method,
        payment_status="Pending" if payment_method == "cod" else "Paid"
    )

    for item in cart_items:
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

    cart_items.delete()

    send_mail(
        'Order Confirmation',
        f'Hi {name}, your order #{order.id} has been placed successfully. Total: ₹{total_price}',
        'noreply@bagstore.com',
        [email],
        fail_silently=True,
    )

    return Response({
        'message': 'Order placed successfully',
        'order_id': order.id,
        'payment_method': payment_method,
        'payment_status': order.payment_status
    })

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Order

@api_view(["POST"])
def create_order(request):
    data = request.data
    order = Order.objects.create(
        name=data["name"],
        email=data["email"],
        address=data["address"],
        payment_method=data["payment_method"],
        card_details=data["card_details"],  # Ideally masked
        items=data["items"],
        total=data["total"],
    )
    return Response({"message": "Order placed successfully", "order_id": order.id})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order, OrderItem, Product
import json

@csrf_exempt  # temporarily disables CSRF for testing
def place_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Validate required fields
            if not data.get('customer_name') or not data.get('customer_email') or not data.get('customer_address'):
                return JsonResponse({'success': False, 'error': 'Name, email, and address are required.'})

            cart_items = data.get("cartItems", [])
            if not cart_items:
                return JsonResponse({'success': False, 'error': 'Cart is empty.'})

            # Create order
            order = Order.objects.create(
                name=data['customer_name'],
                email=data['customer_email'],
                address=data['customer_address'],
                payment_method=data['payment_method'],
                card_details=data.get('card_details'),
                total=data['total']
            )

            # Create order items
            for item in cart_items:
                product_id = item.get('product_id')
                quantity = item.get('quantity', 1)
                product = Product.objects.get(id=product_id)
                OrderItem.objects.create(order=order, product=product, quantity=quantity)

            return JsonResponse({'success': True, 'order_id': order.id})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


def orders_list(request):
    if request.method == "GET":
        try:
            orders = Order.objects.all().order_by('-created_at')
            orders_data = []

            for order in orders:
                items = []
                for item in order.order_items.all():
                    items.append({
                        'id': item.id,
                        'product_name': item.product.name,
                        'quantity': item.quantity,
                        'price': item.product.price
                    })

                orders_data.append({
                    'id': order.id,
                    'customer_name': order.name,
                    'customer_email': order.email,
                    'customer_address': order.address,
                    'payment_method': order.payment_method,
                    'total': order.total,
                    'order_items': items
                })

            return JsonResponse({'orders': orders_data})

        except Exception as e:
            return JsonResponse({'error': str(e)})


from .models import Order
from django.http import JsonResponse

def get_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    orders_list = [
        {
            "id": o.id,
            "name": o.name,
            "email": o.email,
            "address": o.address,
            "items": o.items,
            "total": float(o.total),
            "payment_method": o.payment_method,
            "card_details": o.card_details,
            "created_at": o.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for o in orders
    ]
    return JsonResponse(orders_list, safe=False)
