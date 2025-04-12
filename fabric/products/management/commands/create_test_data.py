# products/management/commands/create_test_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from products.models import Supplier, Customer, Product, Sale, Payment, Order
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create test data for the application'

    def handle(self, *args, **kwargs):
        # Mevcut verileri sil
        self.clear_data()

        # Yeni test verilerini oluştur
        self.create_test_data()

        self.stdout.write(self.style.SUCCESS('Test verileri başarıyla oluşturuldu.'))

    def clear_data(self):
        # Tüm verileri sil
        Sale.objects.all().delete()
        Payment.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()
        Customer.objects.all().delete()
        Supplier.objects.all().delete()

    def create_test_data(self):
        # Tedarikçi verileri oluştur
        suppliers = [
            Supplier.objects.create(name='ABC Tekstil', phone='1234567890', email='abc@textile.com', address='İstanbul'),
            Supplier.objects.create(name='XYZ Kumaş', phone='0987654321', email='xyz@fabric.com', address='Ankara'),
            Supplier.objects.create(name='123 Dokuma', phone='5555555555', email='123@weave.com', address='İzmir'),
        ]

        # Müşteri verileri oluştur
        customers = [
            Customer.objects.create(name='Ahmet Yılmaz'),
            Customer.objects.create(name='Mehmet Demir'),
            Customer.objects.create(name='Ayşe Kaya'),
        ]

        # Ürün verileri oluştur
        products = []
        for supplier in suppliers:
            for i in range(3):  # Her tedarikçi için 3 ürün
                product = Product.objects.create(
                    name=f'Ürün {i + 1} - {supplier.name}',
                    supplier_product_name=f'Tedarikçi Ürün {i + 1}',
                    supplier=supplier,
                    purchase_price=Decimal(random.uniform(10, 100)),
                    sale_price=Decimal(random.uniform(20, 150)),
                    currency='TL'
                )
                products.append(product)

        # Satış verileri oluştur
        for _ in range(10):  # 10 satış
            sale = Sale.objects.create(
                product=random.choice(products),
                customer=random.choice(customers),
                sale_price=Decimal(random.uniform(20, 150)),
                meters=Decimal(random.uniform(1, 10)),
                currency='TL',
                date=timezone.now(),
                is_paid=random.choice([True, False])
            )

            # Ödeme verileri oluştur
            Payment.objects.create(
                sale=sale,
                amount=Decimal(random.uniform(10, float(sale.sale_price) * float(sale.meters))),  # float dönüşümü
                currency='TL',
                date=timezone.now(),
                status=random.choice(['paid', 'pending']),
                notes='Test ödemesi'
            )

        # Sipariş verileri oluştur
        for _ in range(5):  # 5 sipariş
            Order.objects.create(
                product=random.choice(products),
                customer=random.choice(customers),
                supplier=random.choice(suppliers),
                meters=Decimal(random.uniform(1, 10)),
                deadline_date=timezone.now().date() + timezone.timedelta(days=random.randint(1, 30)),
                purchase_price=Decimal(random.uniform(10, 100)),
                sale_price=Decimal(random.uniform(20, 150)),
                currency='TL',
                notes='Test siparişi'
            )