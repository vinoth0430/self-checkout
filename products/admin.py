from django.contrib import admin
from django.utils.html import format_html
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'barcode', 'price', 'gst_rate', 'stock_display')
    list_editable = ('price', 'gst_rate')
    list_filter = ('gst_rate',)
    search_fields = ('name', 'barcode')
    ordering = ('name',)

    def stock_display(self, obj):
        color = '#DC2626' if obj.stock < 10 else '#16A34A'
        return format_html('<b style="color:{}">{}</b>', color, obj.stock)
    stock_display.short_description = 'Stock'

class Media:
    css = {'all': ('admin_theme.css',)}