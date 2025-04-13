from django.urls import path
from . import views

urlpatterns = [
 # Ana Sayfa
    path('', views.home, name='home'),
    # Ürün işlemleri
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/delete/', views.delete_product, name='delete_product'),
    # Satış işlemleri artık sipariş işlemleri ile birleştirildi
    # Ödeme işlemleri
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/add/', views.add_payment, name='add_payment'),
    # Raporlar
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('reports/purchases/', views.purchase_report, name='purchase_report'),
    path('reports/profit/', views.profit_report, name='profit_report'),
    # Tedarikçi URL'leri
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('suppliers/<int:supplier_id>/delete/', views.delete_supplier, name='delete_supplier'),
    # API Endpoint'leri
    path('api/product/<int:product_id>/price/', views.get_product_price, name='get_product_price'),
    path('api/sales-summary/', views.sales_summary_api, name='sales_summary_api'),
    path('api/products/', views.api_products_by_category, name='api_products_by_category'),
    # Sipariş işlemleri
    path('orders/', views.order_list, name='order_list'),
    path('orders/add/', views.add_order, name='add_order'),
    path('orders/<int:pk>/update-status/', views.update_order_status, name='update_order_status'),
    path('orders/<int:pk>/delete/', views.delete_order, name='delete_order'),
]
