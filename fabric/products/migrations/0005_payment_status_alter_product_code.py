# Generated by Django 5.2 on 2025-04-10 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_product_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='product',
            name='code',
            field=models.CharField(editable=False, max_length=50, unique=True, verbose_name='Ürün Kodu'),
        ),
    ]
