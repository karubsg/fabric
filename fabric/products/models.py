from django.db import models
import random
# Create your models here.
from django.db import models
from django.utils import timezone

# Para birimleri için seçenekler
CURRENCY_CHOICES = [
    ('₺', '₺ (TL)'),
    ('$', '$ (USD)'),
    ('€', '€ (EUR)'),
]

from django.db import models

class Currency(models.Model):
    name = models.CharField(max_length=10, unique=True)  # Örn: USD, EUR
    rate = models.DecimalField(max_digits=10, decimal_places=4)  # TL cinsinden kur (örn: 32.1500)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.rate}"

class Supplier(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Tedarikçi Adı')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefon')
    email = models.EmailField(blank=True, null=True, verbose_name='E-posta')
    address = models.TextField(blank=True, null=True, verbose_name='Adres')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tedarikçi'
        verbose_name_plural = 'Tedarikçiler'
        ordering = ['name']

class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Firma Ürün Adı')
    supplier_product_name = models.CharField(max_length=100, verbose_name='Tedarikçi Ürün Adı')
    code = models.CharField(max_length=20, verbose_name='Ürün Kodu')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name='Tedarikçi')
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Alış Fiyatı')
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Satış Fiyatı')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='TL', verbose_name='Para Birimi')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.code:
            last_product = Product.objects.order_by('-id').first()
            if last_product:
                last_number = int(last_product.code.split('-')[1])
                self.code = f"URUN-{str(last_number + 1).zfill(4)}"
            else:
                self.code = "URUN-0001"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        unique_together = ['name']  # Firma ürün adı benzersiz olmalı
        verbose_name = 'Ürün'
        verbose_name_plural = 'Ürünler'
        ordering = ['-created_at']

class Customer(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Ürün", related_name="sales")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Müşteri")
    sale_price = models.DecimalField("Satış Fiyatı (Metre)", max_digits=10, decimal_places=2)
    currency = models.CharField("Para Birimi", max_length=3, choices=CURRENCY_CHOICES)
    meters = models.DecimalField("Metre", max_digits=10, decimal_places=2)
    date = models.DateField("Satış Tarihi")
    is_paid = models.BooleanField("Tamamen Ödendi mi?", default=False)
    total_amount = models.DecimalField("Toplam Tutar", max_digits=10, decimal_places=2, editable=False)
    remaining_payment = models.DecimalField("Kalan Ödeme", max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme Tarihi", auto_now=True)

    def save(self, *args, **kwargs):
        # Toplam tutarı hesapla
        self.total_amount = self.sale_price * self.meters
        
        # İlk kayıtta kalan ödemeyi toplam tutara eşitle
        if not self.pk:  # Yeni kayıt
            self.remaining_payment = self.total_amount
            
        super().save(*args, **kwargs)

    def update_payment_status(self):
        # Toplam ödemeleri hesapla
        total_payments = Payment.objects.filter(sale=self).aggregate(
            total=models.Sum('amount'))['total'] or 0
        
        # Kalan ödemeyi güncelle
        self.remaining_payment = self.total_amount - total_payments
        
        # Ödeme durumunu kontrol et
        self.is_paid = (self.remaining_payment <= 0)
        self.save()

    def __str__(self):
        return f"{self.customer.name} - {self.product.name} - {self.date}"

    class Meta:
        verbose_name = "Satış"
        verbose_name_plural = "Satışlar"
        ordering = ['-date']

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Beklemede'),
        ('paid', 'Ödendi'),
        ('cancelled', 'İptal Edildi'),
    ]

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, verbose_name="Satış")
    amount = models.DecimalField("Ödeme Tutarı", max_digits=10, decimal_places=2)
    currency = models.CharField("Para Birimi", max_length=3, choices=CURRENCY_CHOICES)
    date = models.DateField("Ödeme Tarihi")
    status = models.CharField(
        "Durum",
        max_length=20,
        choices=PAYMENT_STATUS,
        default='paid'
    )
    notes = models.TextField("Notlar", blank=True, null=True)
    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme Tarihi", auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Satışın ödeme durumunu güncelle
        self.sale.update_payment_status()

    def __str__(self):
        return f"{self.sale} - {self.amount} {self.currency}"

    class Meta:
        verbose_name = "Ödeme"
        verbose_name_plural = "Ödemeler"
        ordering = ['-date']

class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Beklemede'),
        ('confirmed', 'Tedarikçi Onayladı'),
        ('in_production', 'Üretimde'),
        ('ready', 'Hazır'),
        ('delivered', 'Teslim Alındı'),
        ('delayed', 'Gecikti'),
        ('cancelled', 'İptal Edildi'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Ürün", related_name="purchases")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Müşteri")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="Tedarikçi")
    order_date = models.DateField("Sipariş Tarihi", auto_now_add=True)
    deadline_date = models.DateField("Termin Tarihi")
    meters = models.DecimalField("Metre", max_digits=10, decimal_places=2)
    status = models.CharField("Durum", max_length=20, choices=ORDER_STATUS, default='pending')
    purchase_price = models.DecimalField("Alış Fiyatı (Metre)", max_digits=10, decimal_places=2)
    sale_price = models.DecimalField("Satış Fiyatı (Metre)", max_digits=10, decimal_places=2)
    currency = models.CharField("Para Birimi", max_length=3, choices=CURRENCY_CHOICES)
    notes = models.TextField("Notlar", blank=True, null=True)
    last_status_update = models.DateTimeField("Son Durum Güncellemesi", auto_now=True)
    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme Tarihi", auto_now=True)

    def save(self, *args, **kwargs):
        # Eğer durum güncellenmediyse ve termin tarihine 3 gün veya daha az kaldıysa
        if self.status not in ['ready', 'delivered', 'cancelled']:
            today = timezone.now().date()
            days_until_deadline = (self.deadline_date - today).days
            if days_until_deadline <= 3:
                self.status = 'delayed'
        super().save(*args, **kwargs)

    def total_purchase_amount(self):
        return self.purchase_price * self.meters

    def total_sale_amount(self):
        return self.sale_price * self.meters

    def expected_profit(self):
        return self.total_sale_amount() - self.total_purchase_amount()

    def days_until_deadline(self):
        today = timezone.now().date()
        return (self.deadline_date - today).days

    def is_delayed(self):
        return self.days_until_deadline() < 0

    def __str__(self):
        return f"{self.customer.name} - {self.product.name} ({self.meters} metre) - {self.get_status_display()}"

    class Meta:
        verbose_name = "Sipariş"
        verbose_name_plural = "Siparişler"
        ordering = ['-order_date']
