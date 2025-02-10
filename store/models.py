from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Size(models.Model):
    name = models.CharField(max_length=20)  # e.g., S, M, L, XL, XXL
    
    def __str__(self):
        return self.name

class Pincode(models.Model):
    code = models.CharField(max_length=6)
    is_deliverable = models.BooleanField(default=True)
    delivery_days = models.IntegerField(default=3)
    
    def __str__(self):
        return f"{self.code} ({'Deliverable' if self.is_deliverable else 'Not Deliverable'})"

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    sizes = models.ManyToManyField(Size, through='ProductSize')

    def __str__(self):
        return self.name

    def get_final_price(self):
        return self.discount_price if self.discount_price else self.price

    def has_discount(self):
        return bool(self.discount_price and self.discount_price < self.price)

    class Meta:
        ordering = ['-created_at']

class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['product', 'size']
    
    def __str__(self):
        return f"{self.product.name} - {self.size.name} ({self.stock} in stock)"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pincode = models.CharField(max_length=6, null=True, blank=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'product', 'size']

    def __str__(self):
        return f"{self.quantity}x {self.product.name} ({self.size.name})"

    def get_total_price(self):
        return self.quantity * self.product.get_final_price()

class Review(models.Model):
    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # One review per product per user

    def __str__(self):
        return f'{self.user.username} - {self.product.name} - {self.rating} stars'
