# products/management/commands/create_test_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from products.models import Supplier, Customer, Product, Sale, Payment, Order, Currency
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create comprehensive test data for the application'

    def handle(self, *args, **kwargs):
        # Clear existing data
        self.clear_data()

        # Create new test data
        self.create_test_data()

        self.stdout.write(self.style.SUCCESS('Gerçekçi test verileri başarıyla oluşturuldu.'))

    def clear_data(self):
        Sale.objects.all().delete()
        Payment.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()
        Customer.objects.all().delete()
        Supplier.objects.all().delete()
        Currency.objects.all().delete()

    def create_test_data(self):
        # Güncel döviz kurlarını oluştur
        Currency.objects.create(name='USD', rate=Decimal('32.15'))
        Currency.objects.create(name='EUR', rate=Decimal('34.75'))
        
        # Türk tedarikçi firmaları
        turkish_suppliers = [
            {'name': 'Akın Tekstil A.Ş.', 'phone': '0212 555 1001', 'email': 'info@akintekstil.com', 'address': 'İstanbul, Türkiye'},
            {'name': 'Yıldız Kumaş Ltd. Şti.', 'phone': '0232 444 2002', 'email': 'satis@yildizkumas.com', 'address': 'İzmir, Türkiye'},
            {'name': 'Bursa İplik Sanayi', 'phone': '0224 333 3003', 'email': 'iletisim@bursaiplik.com', 'address': 'Bursa, Türkiye'},
            {'name': 'Denizli Dokuma A.Ş.', 'phone': '0258 222 4004', 'email': 'info@denizlidokuma.com', 'address': 'Denizli, Türkiye'},
            {'name': 'Gaziantep Tekstil San. Tic.', 'phone': '0342 111 5005', 'email': 'satis@gazianteptekstil.com', 'address': 'Gaziantep, Türkiye'}
        ]
        
        # Yabancı müşteri firmaları
        foreign_customers = [
            'Textile World GmbH',
            'Fashion Fabrics Inc.',
            'Milano Tessuti S.p.A.',
            'London Textile Trading Ltd.',
            'Paris Mode Fabrics',
            'Barcelona Textiles',
            'New York Garment Co.',
            'Dubai Fabric Market LLC',
            'Berlin Fashion House',
            'Amsterdam Textile Group'
        ]
        
        # Çiçek isimleri (tedarikçi ürün adları için)
        flower_names = [
            'Gül', 'Lale', 'Papatya', 'Orkide', 'Menekşe', 'Zambak', 'Karanfil',
            'Sümbül', 'Nergis', 'Yasemin', 'Lavanta', 'Mimoza', 'Manolya', 'Açelya'
        ]
        
        # Şehir isimleri (firma ürün adları için)
        city_names = [
            'İstanbul', 'Paris', 'Londra', 'New York', 'Tokyo', 'Roma', 'Berlin',
            'Madrid', 'Barselona', 'Viyana', 'Amsterdam', 'Prag', 'Venedik', 'Dubai'
        ]
        
        # Kumaş renkleri
        colors = [
            'Kırmızı', 'Mavi', 'Yeşil', 'Siyah', 'Beyaz', 'Gri', 'Lacivert',
            'Bordo', 'Mor', 'Turkuaz', 'Bej', 'Haki', 'Sarı', 'Turuncu'
        ]
        
        # Tedarikçileri oluştur
        suppliers = []
        for supplier_data in turkish_suppliers:
            supplier = Supplier.objects.create(
                name=supplier_data['name'],
                phone=supplier_data['phone'],
                email=supplier_data['email'],
                address=supplier_data['address']
            )
            suppliers.append(supplier)

        # Müşterileri oluştur
        customers = []
        for customer_name in foreign_customers:
            customer = Customer.objects.create(name=customer_name)
            customers.append(customer)

        # Ürünleri oluştur
        products = []
        for supplier in suppliers:
            # Her tedarikçi için 3 ürün oluştur
            for i in range(3):
                # Tedarikçi ürün adı için çiçek ismi kullan
                flower_name = random.choice(flower_names)
                # Firma ürün adı için şehir ismi kullan
                city_name = random.choice(city_names)
                # Renk seç
                color = random.choice(colors)
                
                # Benzersiz ürün adı oluştur
                unique_name = f"{city_name} {supplier.name.split()[0]} {i+1}"
                
                # Alış fiyatı ve para birimi
                purchase_price = Decimal(random.uniform(10, 100)).quantize(Decimal('0.01'))
                purchase_currency = random.choice(['TL', 'USD'])
                
                # Satış fiyatı (alış fiyatından %30-50 daha yüksek)
                profit_margin = Decimal(random.uniform(1.3, 1.5))
                sale_price = (purchase_price * profit_margin).quantize(Decimal('0.01'))
                
                product = Product.objects.create(
                    name=unique_name,
                    supplier_product_name=f'{flower_name} {i+1}',
                    supplier=supplier,
                    color=color,
                    purchase_price=purchase_price,
                    sale_price=sale_price,
                    currency=purchase_currency
                )
                products.append(product)

        # Satışları oluştur
        for _ in range(20):
            product = random.choice(products)
            customer = random.choice(customers)
            
            # Satış para birimi (USD veya EUR)
            sale_currency = random.choice(['USD', 'EUR'])
            
            # Satış fiyatı (ürün satış fiyatından %10-20 daha yüksek)
            sale_price_margin = Decimal(random.uniform(1.1, 1.2))
            sale_price = (product.sale_price * sale_price_margin).quantize(Decimal('0.01'))
            
            # Metre miktarı
            meters = Decimal(random.uniform(1, 10)).quantize(Decimal('0.01'))
            
            # Satış tarihi (son 1 yıl içinde)
            sale_date = timezone.now().date() - timezone.timedelta(days=random.randint(0, 365))
            
            sale = Sale.objects.create(
                product=product,
                customer=customer,
                sale_price=sale_price,
                meters=meters,
                currency=sale_currency,
                date=sale_date,
                is_paid=False  # Başlangıçta ödenmemiş olarak ayarla
            )
            
            # Toplam tutarı hesapla
            total_amount = sale.sale_price * sale.meters
            
            # Bazı satışlar için kısmi ödeme oluştur
            if random.choice([True, False]):
                # Kısmi ödeme (toplam tutarın %30-90'ı)
                payment_percentage = Decimal(random.uniform(0.3, 0.9))
                payment_amount = (total_amount * payment_percentage).quantize(Decimal('0.01'))
                
                # Ödeme tarihi (satış tarihinden sonra 1-30 gün)
                payment_date = sale_date + timezone.timedelta(days=random.randint(1, 30))
                
                Payment.objects.create(
                    sale=sale,
                    amount=payment_amount,
                    currency=sale_currency,
                    date=payment_date,
                    status='paid',
                    notes=f'{customer.name} firmasından kısmi ödeme'
                )
                
                # Satışın ödeme durumunu güncelle
                sale.update_payment_status()
            
            # Bazı satışlar için tam ödeme oluştur
            elif random.choice([True, False]):
                Payment.objects.create(
                    sale=sale,
                    amount=total_amount,
                    currency=sale_currency,
                    date=sale_date + timezone.timedelta(days=random.randint(1, 15)),
                    status='paid',
                    notes=f'{customer.name} firmasından tam ödeme'
                )
                
                # Satışın ödeme durumunu güncelle
                sale.update_payment_status()

        # Siparişleri oluştur
        for _ in range(15):
            product = random.choice(products)
            customer = random.choice(customers)
            supplier = product.supplier
            
            # Sipariş miktarı
            meters = Decimal(random.uniform(5, 20)).quantize(Decimal('0.01'))
            
            # Termin tarihi (bugünden 7-60 gün sonra)
            deadline_date = timezone.now().date() + timezone.timedelta(days=random.randint(7, 60))
            
            # Alış ve satış fiyatları
            purchase_price = Decimal(random.uniform(15, 80)).quantize(Decimal('0.01'))
            sale_price = (purchase_price * Decimal(random.uniform(1.3, 1.6))).quantize(Decimal('0.01'))
            
            # Para birimi
            currency = random.choice(['TL', 'USD', 'EUR'])
            
            # Sipariş durumu
            status = random.choice(['pending', 'confirmed', 'in_production', 'ready', 'delivered'])
            
            Order.objects.create(
                product=product,
                customer=customer,
                supplier=supplier,
                meters=meters,
                deadline_date=deadline_date,
                purchase_price=purchase_price,
                sale_price=sale_price,
                currency=currency,
                status=status,
                notes=f'{customer.name} firması için {product.name} siparişi'
            )
        
        self.stdout.write(self.style.SUCCESS(f'{len(suppliers)} tedarikçi, {len(customers)} müşteri, {len(products)} ürün oluşturuldu.'))
        self.stdout.write(self.style.SUCCESS(f'{Sale.objects.count()} satış ve {Order.objects.count()} sipariş kaydı oluşturuldu.'))
        self.stdout.write(self.style.SUCCESS(f'{Payment.objects.count()} ödeme kaydı oluşturuldu.'))