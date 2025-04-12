from django.contrib import admin
from .models import Supplier, Product, Customer, Sale, Payment

# Register your models here.
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'supplier', 'purchase_price', 'currency', 'sale_price')  # sale_price alanını buraya ekledik
    list_filter = ('supplier', 'currency')
    search_fields = ('name',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('product', 'customer', 'sale_price', 'currency', 'meters', 'date', 'is_paid')
    list_filter = ('customer', 'product', 'currency', 'is_paid')
    search_fields = ('customer__name', 'product__name')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('sale', 'amount', 'currency', 'date')
    list_filter = ('currency',)
