from django.contrib import admin
from .models import Transaction, TransactionItem

class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'quantity', 'price_at_sale', 'gst_at_sale')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'grand_total', 'customer_email', 'created_at', 'razorpay_payment_id')
    list_filter = ('created_at',)
    search_fields = ('customer_email', 'razorpay_payment_id')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    inlines = [TransactionItemInline]
    readonly_fields = ('razorpay_order_id', 'razorpay_payment_id', 'subtotal', 'gst_total', 'grand_total', 'created_at')

class Media:
    css = {'all': ('admin_theme.css',)}