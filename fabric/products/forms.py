# products/forms.py
from django import forms
from .models import Product, Sale, Payment, Supplier, Customer, Order
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from django.utils import timezone

# CURRENCY_CHOICES'ı burada tanımlıyoruz
CURRENCY_CHOICES = [
    ('TL', 'Türk Lirası'),
    ('USD', 'Amerikan Doları'),
    ('EUR', 'Euro'),
]

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['supplier_product_name', 'name', 'supplier']
        labels = {
            'supplier_product_name': 'Tedarikçi Ürün Adı',
            'name': 'Firma Ürün Adı',
            'supplier': 'Tedarikçi'
        }
        widgets = {
            'supplier_product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tedarikçinin ürün adını giriniz'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sizin vereceğiniz ürün adını giriniz'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'currency': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('supplier_product_name', css_class='form-group col-md-6 mb-3'),
                Column('name', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('supplier', css_class='form-group col-md-12 mb-3'),
                css_class='form-row'
            )
        )

    # Tedarikçi için özel alan
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(), label="Tedarikçi")

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'customer', 'sale_price', 'meters', 'currency', 'date', 'is_paid']
        labels = {
            'product': 'Ürün',
            'customer': 'Müşteri',
            'sale_price': 'Satış Fiyatı',
            'meters': 'Metre',
            'currency': 'Para Birimi',
            'date': 'Satış Tarihi',
            'is_paid': 'Ödenmiş mi?'
        }
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'meters': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control datepicker', 'autocomplete': 'off'}),
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def clean_sale_price(self):
        sale_price = self.cleaned_data.get('sale_price')
        if sale_price <= 0:
            raise forms.ValidationError("Satış fiyatı 0'dan küçük olamaz!")
        return sale_price

    def clean_meters(self):
        meters = self.cleaned_data.get('meters')
        if meters <= 0:
            raise forms.ValidationError("Metre miktarı 0'dan küçük olamaz!")
        return meters

class PaymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sadece ödenmemiş satışları göster ve kalan ödeme bilgisini ekle
        unpaid_sales = Sale.objects.filter(is_paid=False)
        sale_choices = []
        for sale in unpaid_sales:
            remaining = sale.remaining_payment
            sale_text = f"{sale.customer.name} - {sale.product.name} - Kalan: {sale.currency}{remaining:,.2f}"
            sale_choices.append((sale.id, sale_text))
        self.fields['sale'].choices = sale_choices

    class Meta:
        model = Payment
        fields = ['sale', 'amount', 'currency', 'date', 'status', 'notes']
        labels = {
            'sale': 'Satış',
            'amount': 'Ödeme Tutarı',
            'currency': 'Para Birimi',
            'date': 'Ödeme Tarihi',
            'status': 'Durum',
            'notes': 'Notlar'
        }
        widgets = {
            'sale': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Ödeme miktarı 0'dan büyük olmalıdır.")
        return amount

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'phone', 'email', 'address']
        labels = {
            'name': 'Tedarikçi Adı',
            'phone': 'Telefon',
            'email': 'E-posta',
            'address': 'Adres'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'customer', 'supplier', 'meters', 'deadline_date', 
                 'purchase_price', 'sale_price', 'currency', 'notes']
        widgets = {
            'deadline_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        deadline_date = cleaned_data.get('deadline_date')
        if (deadline_date and deadline_date < timezone.now().date()):
            raise forms.ValidationError("Termin tarihi geçmiştir!")
        return cleaned_data
