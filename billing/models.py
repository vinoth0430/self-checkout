from django.db import models
from products.models import Product

class Transaction(models.Model):
    razorpay_order_id = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    customer_email = models.EmailField(blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    gst_total = models.DecimalField(max_digits=10, decimal_places=2)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Txn {self.id} - ₹{self.grand_total} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, related_name='line_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    price_at_sale = models.DecimalField(max_digits=10, decimal_places=2)
    gst_at_sale = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"