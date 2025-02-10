from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Product, Review, Cart, CartItem, Pincode

# Create your views here.

def product_list(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(is_active=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    
    context = {
        'products': products,
        'search_query': query
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    user_has_reviewed = False
    
    if request.user.is_authenticated:
        user_has_reviewed = Review.objects.filter(product=product, user=request.user).exists()
    
    context = {
        'product': product,
        'user_has_reviewed': user_has_reviewed
    }
    return render(request, 'store/product_detail.html', context)

def check_pincode(request, pincode):
    try:
        pincode_obj = Pincode.objects.get(code=pincode)
        return JsonResponse({
            'is_deliverable': pincode_obj.is_deliverable,
            'delivery_days': pincode_obj.delivery_days
        })
    except Pincode.DoesNotExist:
        return JsonResponse({
            'is_deliverable': False,
            'message': 'Delivery not available in this area'
        })

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        size_id = request.POST.get('size_id')
        quantity = int(request.POST.get('quantity', 1))
        pincode = request.POST.get('pincode')

        # Validate pincode
        try:
            pincode_obj = Pincode.objects.get(code=pincode)
            if not pincode_obj.is_deliverable:
                messages.error(request, 'Delivery not available in this area')
                return redirect('product_detail', product_id=product_id)
        except Pincode.DoesNotExist:
            messages.error(request, 'Invalid pincode')
            return redirect('product_detail', product_id=product_id)

        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.pincode = pincode
        cart.save()

        # Add item to cart
        try:
            cart_item = CartItem.objects.get(
                cart=cart,
                product=product,
                size_id=size_id
            )
            cart_item.quantity += quantity
            cart_item.save()
            messages.success(request, 'Cart updated successfully!')
        except CartItem.DoesNotExist:
            CartItem.objects.create(
                cart=cart,
                product=product,
                size_id=size_id,
                quantity=quantity
            )
            messages.success(request, 'Product added to cart!')

    return redirect('cart')

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'store/cart.html', {'cart': cart})

@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        action = request.POST.get('action')
        
        if action == 'remove':
            item.delete()
            messages.success(request, 'Item removed from cart!')
        elif action == 'update':
            quantity = int(request.POST.get('quantity', 1))
            if quantity > 0:
                item.quantity = quantity
                item.save()
                messages.success(request, 'Cart updated!')
            else:
                item.delete()
                messages.success(request, 'Item removed from cart!')
    
    return redirect('cart')

@login_required
def add_review(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # Check if user has already reviewed
        if Review.objects.filter(product=product, user=request.user).exists():
            messages.error(request, 'You have already reviewed this product.')
            return redirect('product_detail', product_id=product_id)
        
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating and comment:
            Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                comment=comment
            )
            messages.success(request, 'Thank you for your review!')
        else:
            messages.error(request, 'Please provide both rating and comment.')
            
    return redirect('product_detail', product_id=product_id)

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('product_list')
        else:
            for error in form.errors.values():
                messages.error(request, error[0])
    return render(request, 'store/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('product_list')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'store/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('product_list')

@login_required
def profile_view(request):
    return render(request, 'store/profile.html')

def about_view(request):
    return render(request, 'store/about.html')

def growers_view(request):
    return render(request, 'store/growers.html')

def merchants_view(request):
    return render(request, 'store/merchants.html')

def contact_view(request):
    if request.method == 'POST':
        # Handle contact form submission
        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        return redirect('contact')
    return render(request, 'store/contact.html')
