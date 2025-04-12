from datetime import datetime, date, timedelta
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.utils.formats import number_format
from django.db.models import Sum, Q, Count, F, FloatField, ExpressionWrapper

from .models import Product, Sale, Payment, Supplier, Customer, Currency, Order
from .forms import ProductForm, SaleForm, PaymentForm, SupplierForm, OrderForm

from django.utils import timezone

def format_currency(value, currency):
    if currency == 'USD':
        return f"${number_format(value, decimal_pos=2)}"
    elif currency == 'EUR':
        return f"€{number_format(value, decimal_pos=2)}"
    else:
        return f"₺{number_format(value, decimal_pos=2)}"

# Ana Sayfa - Geliştirilmiş Versiyon
def home(request):
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    # Bugünkü siparişler (sale_price * meters hesaplaması)
    today_orders = Order.objects.filter(
        order_date__gte=today,
        order_date__lt=tomorrow
    ).annotate(
        calculated_total=ExpressionWrapper(
            F('sale_price') * F('meters'),
            output_field=FloatField()
        )
    ).aggregate(total=Sum('calculated_total'))['total'] or 0
    
    # Toplam siparişler
    total_orders = Order.objects.annotate(
        calculated_total=ExpressionWrapper(
            F('sale_price') * F('meters'),
            output_field=FloatField()
        )
    ).aggregate(total=Sum('calculated_total'))['total'] or 0
    
    # Toplam ürün sayısı
    total_products = Product.objects.count()
    
    # Bugünkü ödemeler (Payment modelindeki date alanına göre)
    today_payments = Payment.objects.filter(
        date__gte=today,
        date__lt=tomorrow
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Son 5 sipariş
    recent_orders = Order.objects.select_related('product', 'customer').order_by('-order_date')[:5]

    # Son 5 ödeme
    recent_payments = Payment.objects.select_related('sale').order_by('-date')[:5]

    context = {
        'today_orders': format_currency(today_orders, '₺'),
        'total_orders': format_currency(total_orders, '₺'),
        'total_products': total_products,
        'today_payments': format_currency(today_payments, '₺'),
        'recent_orders': recent_orders,
        'recent_payments': recent_payments,
    }
    return render(request, 'products/home.html', context)

# Ürün Detay View'ı Eklendi
@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    sales = product.sales.all()
    purchases = product.purchases.all()
    
    # Sale modeli için total_amount alanı var, ancak Order modeli için total_purchase_amount ve total_sale_amount metotları kullanılmalı
    # Satışlar için toplam gelir hesaplaması
    total_revenue = 0
    for sale in sales:
        # total_amount bir model alanı olduğu için doğrudan erişebiliriz
        total_revenue += sale.total_amount
    
    # Siparişler için toplam maliyet hesaplaması
    total_cost = 0
    for purchase in purchases:
        total_cost += purchase.total_purchase_amount()
    
    context = {
        'product': product,
        'sales': sales,
        'purchases': purchases,
        'total_sold': sales.aggregate(total=Sum('meters'))['total'] or 0,
        'total_purchased': purchases.aggregate(total=Sum('meters'))['total'] or 0,
        'total_revenue': total_revenue,
        'total_cost': total_cost,
    }
    return render(request, 'products/product_detail.html', context)

# Ürün Silme View'ı Eklendi
@require_http_methods(["POST"])
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, f'"{product.name}" ürünü silindi!')
    return redirect('product_list')

# Satış işlemleri sipariş işlemleri ile birleştirildi

# Ürün İşlemleri
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'"{product.name}" ürünü eklendi!')
            return redirect('product_list')
    else:
        form = ProductForm()
    
    return render(request, 'products/add_product.html', {'form': form})

def product_list(request):
    query = request.GET.get('q')
    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(code__icontains=query) |
            Q(description__icontains=query)
        )
    
    # Gelişmiş sıralama
    sort = request.GET.get('sort', 'name')
    order = request.GET.get('order', 'asc')
    
    if order == 'desc':
        sort = f'-{sort}'
    
    paginator = Paginator(products.order_by(sort), 10)
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
        
    return render(request, 'products/product_list.html', {
        'products': products,
        'search_query': query,
        'sort': sort.replace('-', ''),
        'order': order
    })

# Satış İşlemleri
# Satış işlemleri sipariş işlemleri ile birleştirildi


# Ödeme İşlemleri
def add_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            messages.success(request, f'Ödeme #{payment.id} (₺{payment.amount:,.2f}) alındı')
            return redirect('payment_list')
    else:
        form = PaymentForm()
    
    return render(request, 'products/add_payment.html', {'form': form})

def payment_list(request):
    # Tarih filtrelerini al
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    payments = Payment.objects.all()
    
    # Tarih filtrelemesi
    if start_date:
        payments = payments.filter(date__gte=start_date)
    if end_date:
        payments = payments.filter(date__lte=end_date)
    
    # Toplam hesaplama
    total = payments.aggregate(total=Sum('amount'))['total'] or 0
    
    # Sayfalama
    paginator = Paginator(payments.order_by('-date'), 15)
    page = request.GET.get('page')
    
    try:
        payments = paginator.page(page)
    except PageNotAnInteger:
        payments = paginator.page(1)
    except EmptyPage:
        payments = paginator.page(paginator.num_pages)
        
    context = {
        'payments': payments,
        'total_payments': total,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'products/payment_list.html', context)

# Raporlar
def sales_report(request):
    # Tarih filtresi
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')
    selected_customer = request.GET.get('customer')
    selected_currency = request.GET.get('currency')

    sales = Sale.objects.all()

    # Tarih aralığına göre filtreleme
    if date_from:
        sales = sales.filter(date__gte=date_from)
    if date_to:
        sales = sales.filter(date__lte=date_to)

    # Müşteriye göre filtreleme
    if selected_customer:
        sales = sales.filter(customer__name=selected_customer)

    # Para birimi filtresi
    if selected_currency:
        sales = sales.filter(currency=selected_currency)

    # Bugünkü döviz kurlarını al
    latest_usd = Currency.objects.filter(name='USD').order_by('-date').first()
    latest_eur = Currency.objects.filter(name='EUR').order_by('-date').first()
    
    usd_rate = latest_usd.rate if latest_usd else Decimal('31.00')  # Varsayılan değerler
    eur_rate = latest_eur.rate if latest_eur else Decimal('33.00')  # Varsayılan değerler

    # Her satışın toplamını ve TL karşılığını hesapla
    filtered_sales = []
    total_usd = total_eur = total_try = Decimal('0')
    total_usd_tl = total_eur_tl = Decimal('0')

    for sale in sales:
        total_price = sale.sale_price * sale.meters
        total_price_tl = Decimal('0')

        if sale.currency == 'USD':
            total_usd += total_price
            total_price_tl = total_price * usd_rate
            total_usd_tl += total_price_tl
        elif sale.currency == 'EUR':
            total_eur += total_price
            total_price_tl = total_price * eur_rate
            total_eur_tl += total_price_tl
        else:  # TL
            total_try += total_price
            total_price_tl = total_price

        filtered_sales.append({
            'date': sale.date,
            'customer_name': sale.customer.name,
            'product': sale.product.name,
            'quantity': sale.meters,
            'unit_price': sale.sale_price,
            'currency': sale.get_currency_display(),  # Para birimi görünen adını kullan
            'total_price': total_price,
            'total_price_tl': total_price_tl,
        })

    grand_total_tl = total_usd_tl + total_eur_tl + total_try

    # Mevcut müşterileri dropdown'a göndermek için
    customers = Customer.objects.values_list('name', flat=True).distinct()

    context = {
        'filtered_sales': filtered_sales,
        'total_usd': total_usd,
        'total_eur': total_eur,
        'total_try': total_try,
        'total_usd_tl': total_usd_tl,
        'total_eur_tl': total_eur_tl,
        'grand_total_tl': grand_total_tl,
        'date_from': date_from,
        'date_to': date_to,
        'selected_customer': selected_customer,
        'selected_currency': selected_currency,
        'customers': customers,
    }
    return render(request, 'products/sales_report.html', context)



def get_product_price(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return JsonResponse({'price': float(product.price)})

def sales_summary_api(request):
    today = datetime.now().date()
    last_week = today - timedelta(days=7)
    
    data = {
        # Bugün satışları
        'today_sales': Sale.objects.filter(date__exact=today)
            .annotate(total_amount=F('sale_price') * F('meters'))
            .aggregate(total=Sum('total_amount'))['total'] or 0,
        
        # Geçen hafta satışları
        'weekly_sales': Sale.objects.filter(date__gte=last_week)  # `date__gte=last_week` kullanıyoruz
            .annotate(total_amount=F('sale_price') * F('meters'))  # `total_amount` hesaplama
            .aggregate(total=Sum('total_amount'))['total'] or 0,
        
        # Toplam ürün sayısı
        'total_products': Product.objects.count(),
        
        # Bekleyen ödemeler
        'pending_payments': Payment.objects.filter(status='pending').count()
    }
    
    return JsonResponse(data)

def api_products_by_category(request):
    category_id = request.GET.get('category_id')
    products = Product.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(products), safe=False)

def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'products/supplier_list.html', {
        'suppliers': suppliers
    })

def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tedarikçi başarıyla eklendi.')
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'products/add_supplier.html', {'form': form})

def delete_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Tedarikçi başarıyla silindi.')
    return redirect('supplier_list')

@login_required
def order_list(request):
    status = request.GET.get('status', 'all')
    orders = Order.objects.select_related('customer', 'product', 'supplier').order_by('-created_at')
    
    if status != 'all':
        orders = orders.filter(status=status)
    
    form = OrderForm()
    
    context = {
        'orders': orders,
        'form': form,
        'status': status,
        'order': {'ORDER_STATUS': Order.ORDER_STATUS}  # ORDER_STATUS seçeneklerini template'e gönder
    }
    return render(request, 'products/order_list.html', context)

@login_required
def add_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            messages.success(request, 'Sipariş başarıyla oluşturuldu.')
            return redirect('order_list')
        else:
            messages.error(request, 'Lütfen formu kontrol ediniz.')
    return redirect('order_list')

@login_required
def update_order_status(request, pk):
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=pk)
        new_status = request.POST.get('status')
        note = request.POST.get('note', '')
        
        if new_status in dict(Order.ORDER_STATUS):
            order.status = new_status
            order.notes = note if note else order.notes
            order.last_status_update = timezone.now()
            order.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            else:
                messages.success(request, 'Sipariş durumu güncellendi.')
                
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Geçersiz durum.'})
            else:
                messages.error(request, 'Geçersiz durum.')
                
    return redirect('order_list')

@login_required
def delete_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Sipariş başarıyla silindi.')
    return redirect('order_list')

@login_required
def delete_sale(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        sale.delete()
        messages.success(request, 'Satış başarıyla silindi.')
        return redirect('sale_list')
    return redirect('sale_list')