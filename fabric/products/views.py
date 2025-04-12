from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.db.models import Sum, Q, Count
from datetime import datetime, timedelta
from django.views.decorators.http import require_http_methods
from .forms import ProductForm, SaleForm, PaymentForm, SupplierForm
from .models import Product, Sale, Payment, Supplier
from django.http import JsonResponse
from django.http import JsonResponse
from django.db.models import Sum
from datetime import datetime, timedelta
from django.shortcuts import render
from .models import Sale, Currency
from django.db.models import Sum, F, FloatField
from django.utils.timezone import now
from datetime import datetime
from django.shortcuts import render
from django.db.models import Sum
from datetime import date
from .models import Sale, Product, Payment
from django.shortcuts import render
from django.db.models import Sum, F, ExpressionWrapper, FloatField
from datetime import date
from .models import Sale, Product, Payment
from django.shortcuts import render
from django.db.models import Sum, F, ExpressionWrapper, FloatField
from datetime import date
from .models import Sale, Product, Payment
from django.db.models import Sum
from django.db.models import Sum, F
from django.utils import timezone
from datetime import timedelta
from datetime import datetime, timedelta
from django.db.models import F, Sum
from django.http import JsonResponse
from .models import Sale, Product, Payment
from django.contrib.auth.decorators import login_required
from .models import Order
from .forms import OrderForm

# Ana Sayfa - Geliştirilmiş Versiyon
def home(request):
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    # Bugünkü satışlar (sale_price * meters hesaplaması)
    today_sales = Sale.objects.filter(
        date__gte=today,
        date__lt=tomorrow
    ).annotate(
        calculated_total=ExpressionWrapper(
            F('sale_price') * F('meters'),
            output_field=FloatField()
        )
    ).aggregate(total=Sum('calculated_total'))['total'] or 0
    
    # Toplam satışlar
    total_sales = Sale.objects.annotate(
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
    
    context = {
        'today_sales': round(float(today_sales), 2),
        'total_sales': round(float(total_sales), 2),
        'total_products': total_products,
        'today_payments': round(float(today_payments), 2),
    }
    return render(request, 'products/home.html', context)

# Ürün Detay View'ı Eklendi
@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    sales = product.sales.all()
    purchases = product.purchases.all()
    
    context = {
        'product': product,
        'sales': sales,
        'purchases': purchases,
        'total_sold': sales.aggregate(total=Sum('meters'))['total'] or 0,
        'total_purchased': purchases.aggregate(total=Sum('meters'))['total'] or 0,
        'total_revenue': sales.aggregate(total=Sum('total_amount'))['total'] or 0,
        'total_cost': purchases.aggregate(total=Sum('total_amount'))['total'] or 0,
    }
    return render(request, 'products/product_detail.html', context)

# Ürün Silme View'ı Eklendi
@require_http_methods(["POST"])
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, f'"{product.name}" ürünü silindi!')
    return redirect('product_list')

# Satış İptal View'ı Eklendi
@require_http_methods(["POST"])
def cancel_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    sale.delete()
    messages.warning(request, f'Satış #{sale_id} iptal edildi!')
    return redirect('sale_list')

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
def add_sale(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save()
            messages.success(request, f'Satış #{sale.id} kaydedildi (₺{sale.total_price:,.2f})')
            return redirect('sale_list')
    else:
        form = SaleForm()
    
    return render(request, 'products/add_sale.html', {'form': form})

def sale_list(request):
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')
    
    sales = Sale.objects.all()
    
    if date_from and date_to:
        sales = sales.filter(date__range=[date_from, date_to])
    
    # total_price yerine total_amount() metodunu kullanıyoruz
    total_sales = sales.aggregate(total=Sum(F('sale_price') * F('meters')))['total'] or 0
    paginator = Paginator(sales.order_by('-date'), 15)
    page = request.GET.get('page')
    
    try:
        sales = paginator.page(page)
    except PageNotAnInteger:
        sales = paginator.page(1)
    except EmptyPage:
        sales = paginator.page(paginator.num_pages)
        
    return render(request, 'products/sale_list.html', {
        'sales': sales,
        'total_sales': total_sales,
        'date_from': date_from,
        'date_to': date_to
    })


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
    payments = Payment.objects.all()
    total = payments.aggregate(total=Sum('amount'))['total'] or 0
    
    paginator = Paginator(payments.order_by('-date'), 15)  # 'payment_date' yerine 'date' kullanıldı
    page = request.GET.get('page')
    
    try:
        payments = paginator.page(page)
    except PageNotAnInteger:
        payments = paginator.page(1)
    except EmptyPage:
        payments = paginator.page(paginator.num_pages)
        
    return render(request, 'products/payment_list.html', {
        'payments': payments,
        'total_payments': total
    })

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
        sales = sales.filter(customer__name=selected_customer)  # customer_name yerine customer__name

    # Döviz filtresi
    if selected_currency:
        sales = sales.filter(currency=selected_currency)

    # Bugünkü döviz kurlarını al (günlük en son kayıtları alıyoruz)
    latest_currency = Currency.objects.order_by('-date').first()
    usd_rate = latest_currency.rate if latest_currency and latest_currency.name == 'USD' else 0
    eur_rate = latest_currency.rate if latest_currency and latest_currency.name == 'EUR' else 0

    # Her satışın toplamını ve TL karşılığını hesapla
    filtered_sales = []
    total_usd = total_eur = total_try = 0
    total_usd_tl = total_eur_tl = 0

    for sale in sales:
        total_price = sale.sale_price * sale.meters  # sale_price ve meters kullanılıyor
        total_price_tl = 0

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
            'customer_name': sale.customer.name,  # customer_name yerine customer.name kullanıyoruz
            'product': sale.product.name,  # product adını ekliyoruz
            'quantity': sale.meters,  # quantity yerine meters
            'unit_price': sale.sale_price,  # unit_price yerine sale_price
            'currency': sale.currency,
            'total_price': total_price,
            'total_price_tl': total_price_tl,
        })

    grand_total_tl = total_usd_tl + total_eur_tl + total_try

    # Mevcut müşterileri dropdown'a göndermek için
    customers = Sale.objects.values_list('customer__name', flat=True).distinct()

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
        'status': status
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
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        note = request.POST.get('note', '')
        
        if status in dict(Order.ORDER_STATUS):
            order.status = status
            if note:
                order.notes = f"{order.notes}\n{note}" if order.notes else note
            order.save()
            messages.success(request, 'Sipariş durumu güncellendi.')
        else:
            messages.error(request, 'Geçersiz sipariş durumu.')
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