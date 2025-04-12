# Generated by Django 4.2.7 on 2025-04-10 22:36

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_payment_status_alter_product_code'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payment',
            options={'ordering': ['-date'], 'verbose_name': 'Ödeme', 'verbose_name_plural': 'Ödemeler'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['-created_at'], 'verbose_name': 'Ürün', 'verbose_name_plural': 'Ürünler'},
        ),
        migrations.AlterModelOptions(
            name='sale',
            options={'ordering': ['-date'], 'verbose_name': 'Satış', 'verbose_name_plural': 'Satışlar'},
        ),
        migrations.AddField(
            model_name='payment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Oluşturulma Tarihi'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payment',
            name='notes',
            field=models.TextField(blank=True, null=True, verbose_name='Notlar'),
        ),
        migrations.AddField(
            model_name='payment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi'),
        ),
        migrations.AddField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Oluşturulma Tarihi'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='supplier_product_name',
            field=models.CharField(default='Belirtilmemiş', max_length=100, verbose_name='Tedarikçi Ürün Adı'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi'),
        ),
        migrations.AddField(
            model_name='sale',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Oluşturulma Tarihi'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sale',
            name='remaining_payment',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Kalan Ödeme'),
        ),
        migrations.AddField(
            model_name='sale',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=10, verbose_name='Toplam Tutar'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sale',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Ödeme Tutarı'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='currency',
            field=models.CharField(choices=[('TL', 'Türk Lirası'), ('USD', 'Amerikan Doları'), ('EUR', 'Euro')], max_length=3, verbose_name='Para Birimi'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='date',
            field=models.DateField(verbose_name='Ödeme Tarihi'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='sale',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.sale', verbose_name='Satış'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('pending', 'Beklemede'), ('paid', 'Ödendi'), ('cancelled', 'İptal Edildi')], default='paid', max_length=20, verbose_name='Durum'),
        ),
        migrations.AlterField(
            model_name='product',
            name='currency',
            field=models.CharField(choices=[('TL', 'Türk Lirası'), ('USD', 'Amerikan Doları'), ('EUR', 'Euro')], max_length=3, verbose_name='Para Birimi'),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Firma Ürün Adı'),
        ),
        migrations.AlterField(
            model_name='product',
            name='purchase_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Alış Fiyatı (Metre)'),
        ),
        migrations.AlterField(
            model_name='product',
            name='sale_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Satış Fiyatı (Metre)'),
        ),
        migrations.AlterField(
            model_name='product',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.supplier', verbose_name='Tedarikçi'),
        ),
        migrations.AlterField(
            model_name='sale',
            name='currency',
            field=models.CharField(choices=[('TL', 'Türk Lirası'), ('USD', 'Amerikan Doları'), ('EUR', 'Euro')], max_length=3, verbose_name='Para Birimi'),
        ),
        migrations.AlterField(
            model_name='sale',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.customer', verbose_name='Müşteri'),
        ),
        migrations.AlterField(
            model_name='sale',
            name='date',
            field=models.DateField(verbose_name='Satış Tarihi'),
        ),
        migrations.AlterField(
            model_name='sale',
            name='is_paid',
            field=models.BooleanField(default=False, verbose_name='Tamamen Ödendi mi?'),
        ),
        migrations.AlterField(
            model_name='sale',
            name='meters',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Metre'),
        ),
        migrations.AlterField(
            model_name='sale',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product', verbose_name='Ürün'),
        ),
        migrations.AlterField(
            model_name='sale',
            name='sale_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Satış Fiyatı (Metre)'),
        ),
    ]
