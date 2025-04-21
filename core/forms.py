# from django import forms
# from .models import Client

# class ProductFilterForm(forms.Form):
#     client = forms.ModelChoiceField(
#         queryset=Client.objects.all(),
#         required=False,
#         label="Клиент"
#     )
#     start_date = forms.DateField(
#         required=False,
#         widget=forms.DateInput(attrs={'type': 'date'}),
#         label="С даты"
#     )
#     end_date = forms.DateField(
#         required=False,
#         widget=forms.DateInput(attrs={'type': 'date'}),
#         label="По дату"
#     )
# from django import forms
    
from django import forms
from .models import Client
# from multiprocessing.connection import Client


class ProductFilterForm(forms.Form):
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        required=False,
        label="Клиент",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        required=False,
        label="От даты",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False,
        label="До даты",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    trip_number = forms.CharField(
        required=False,
        label="Номер рейса",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фильтр по рейсу'})
    )

from django.core.validators import FileExtensionValidator
from django.utils import timezone


class ImportProductsForm(forms.Form):
    excel_file = forms.FileField(
        label="Excel файл с товарами",
        validators=[FileExtensionValidator(allowed_extensions=['xlsx'])]
    )
    # Дополнительные поля по необходимости
# class ProductFilterForm(forms.Form):
#     client = forms.ModelChoiceField(
#         queryset=Client.objects.all(),
#         required=False,
#         widget=forms.Select(attrs={
#             'class': 'form-select select2',
#             'data-placeholder': 'Выберите клиента...'
#         }),
#         label="Клиент"
#     )
#     start_date = forms.DateField(
#         required=False,
#         widget=forms.DateInput(attrs={
#             'class': 'form-control',
#             'type': 'date'
#         }),
#         label="От даты"
#     )
#     end_date = forms.DateField(
#         required=False,
#         widget=forms.DateInput(attrs={
#             'class': 'form-control',
#             'type': 'date'
#         }),
#         label="До даты"
#     )

from django import forms
from .models import ProductCategory


class AssignCategoryForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.all(),
        label="Категория товара",
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'category-select'
        })
    )
    
    
from django import forms
from django.core.validators import MinValueValidator

class WithdrawalForm(forms.Form):
    amount = forms.DecimalField(
        label="Сумма",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    description = forms.CharField(
        label="Причина изъятия",
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False
    )