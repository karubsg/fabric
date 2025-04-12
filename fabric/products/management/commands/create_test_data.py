# products/management/commands/create_test_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from products.models import Supplier, Customer, Product, Sale, Payment, Order
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create comprehensive test data for the application'

    def handle(self, *args, **kwargs):
        # Clear existing data
        self.clear_data()

        # Create new test data
        self.create_test_data()

        self.stdout.write(self.style.SUCCESS('Comprehensive test data created successfully.'))

    def clear_data(self):
        Sale.objects.all().delete()
        Payment.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()
        Customer.objects.all().delete()
        Supplier.objects.all().delete()

    def create_test_data(self):
        # Create suppliers
        suppliers = [
            Supplier.objects.create(name=f'Supplier {i}', phone=f'123456789{i}', email=f'supplier{i}@example.com', address=f'Address {i}')
            for i in range(1, 6)
        ]

        # Create customers
        customers = [
            Customer.objects.create(name=f'Customer {i}')
            for i in range(1, 11)
        ]

        # Create products
        products = []
        for supplier in suppliers:
            for i in range(1, 4):
                product = Product.objects.create(
                    name=f'Product {i} - {supplier.name}',
                    supplier_product_name=f'Supplier Product {i}',
                    supplier=supplier,
                    purchase_price=Decimal(random.uniform(10, 100)),
                    sale_price=Decimal(random.uniform(20, 150)),
                    currency='TL'
                )
                products.append(product)

        # Create sales
        for _ in range(20):
            sale = Sale.objects.create(
                product=random.choice(products),
                customer=random.choice(customers),
                sale_price=Decimal(random.uniform(20, 150)),
                meters=Decimal(random.uniform(1, 10)),
                currency='TL',
                date=timezone.now() - timezone.timedelta(days=random.randint(0, 365)),
                is_paid=random.choice([True, False])
            )

            # Create payments for sales
            Payment.objects.create(
                sale=sale,
                amount=Decimal(random.uniform(10, float(sale.sale_price) * float(sale.meters))),
                currency='TL',
                date=timezone.now() - timezone.timedelta(days=random.randint(0, 365)),
                status=random.choice(['paid', 'pending', 'cancelled']),
                notes='Test payment'
            )

        # Create orders
        for _ in range(10):
            Order.objects.create(
                product=random.choice(products),
                customer=random.choice(customers),
                supplier=random.choice(suppliers),
                meters=Decimal(random.uniform(1, 10)),
                deadline_date=timezone.now().date() + timezone.timedelta(days=random.randint(-30, 30)),
                purchase_price=Decimal(random.uniform(10, 100)),
                sale_price=Decimal(random.uniform(20, 150)),
                currency='TL',
                status=random.choice(['pending', 'confirmed', 'in_production', 'ready', 'delivered', 'delayed', 'cancelled']),
                notes='Test order'
            )