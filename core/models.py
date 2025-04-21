from django.db import models
from django.db.models import Sum, Count, Q
from django.contrib.auth.models import User
# Create your models here.
# Клиент
class Client(models.Model):
    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    full_name = models.CharField("ФИО", max_length=255)
    city = models.CharField("Город", max_length=100)
    phone = models.CharField("Телефон", max_length=20)
    no_phone = models.BooleanField("Нет телефона", default=False)
    def __str__(self):
        return self.full_name
    def get_product_stats(self):
        return {
            'total': self.products.count(),
            'awaiting_payment': self.products.filter(status='kassa').count(),
            'sold': self.products.filter(status='sold').count(),
            'debt': self.debts.filter(paid=False).aggregate(Sum('amount'))['amount__sum'] or 0
        }

# Поставка или партия груза
class CargoGroup(models.Model):
    vehicle_number = models.CharField("Номер машины", max_length=50)
    trip_number = models.CharField("Рейс", max_length=50)
    date = models.DateField("Дата поставки")
    
    class Meta:
        verbose_name = "Поставка"
        verbose_name_plural = "Поставки"

    def __str__(self):
        return f"{self.vehicle_number} - {self.trip_number} ({self.date})"
    
class ProductCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

class CashBox(models.Model):
    name = models.CharField("Название кассы", max_length=100)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name="cashboxes")

    class Meta:
        verbose_name = "Касса"
        verbose_name_plural = "Кассы"
        
    def __str__(self):
        return f"{self.category.name} - {self.name}"



# Товар
class Product(models.Model):
    cargo_group = models.ForeignKey(CargoGroup, on_delete=models.CASCADE, related_name='products')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='products')
    name = models.CharField("Наименование товара", max_length=255)
    packaging = models.CharField("Упаковка", max_length=50, blank=True, null=True)
    quantity_places = models.PositiveIntegerField("Количество мест", default=1)
    quantity_kg = models.FloatField("Вес (кг)",default=0, null=True, blank=True)
    quantity_units = models.PositiveIntegerField("Количество (шт)", default=0, null=True, blank=True)
    price = models.FloatField("Цена за единицу ($)", null=True, blank=True)
    total_price = models.DecimalField("Сумма ($)",max_digits=12, decimal_places=2, null=True, blank=True)
    transport_cost = models.FloatField("Йул кира ($)",default=0, null=True, blank=True)
    plomb_number = models.FloatField("Пломба", default=0, blank=True, null=True)
    uzb_price = models.FloatField("УЗБ $", null=True, blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True)
    cashbox = models.ForeignKey(CashBox, on_delete=models.SET_NULL, null=True, blank=True)
    sale_date = models.DateTimeField("Дата продажи", null=True, blank=True)  # Для статистики

    # current_stage = models.ForeignKey(Stage, on_delete=models.SET_NULL, null=True, verbose_name="Текущее местоположение")

    STATUS_CHOICES = [
        ('sklad', 'На складе'),
        ('way', 'В пути'),
        ('kassa', 'На кассе'),
        ('sold', 'Продано'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sklad', db_index=True)
    
    def save(self, *args, **kwargs):
        total = 0

        if self.quantity_kg is not None and self.price is not None:
            total += self.quantity_kg * self.price

        if self.transport_cost != 0:
            total += self.transport_cost

        if self.plomb_number != 0:
            total += self.plomb_number

        self.total_price = total
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    @property
    def get_status_badge(self):
        status_colors = {
            'sklad': 'secondary',
            'way': 'warning',
            'kassa': 'info',
            'sold': 'success'
        }
        return status_colors.get(self.status, 'light')
    def __str__(self):
        return f"{self.name} ({self.client.full_name})"

class FinanceOverview(models.Model):
    date = models.DateField("Дата", auto_now_add=True)
    cash_balance = models.FloatField("Остаток денег", default=0.0)
    product_balance = models.FloatField("Товары на сумму", default=0.0)
    debt_to_us = models.FloatField("Долги нам", default=0.0)
    debt_ours = models.FloatField("Наши долги", default=0.0)

    @property
    def net_assets(self):
        return self.cash_balance + self.product_balance + self.debt_to_us - self.debt_ours
    
    class Meta:
        verbose_name = "Финансовый отчет"
        verbose_name_plural = "Финансовые отчеты"

    def __str__(self):
        return f"Отчет от {self.date}"


class Debt(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='debts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="Сумма долга $")
    is_ours = models.BooleanField("Наш долг?", default=False)  # False = долг клиента перед нами
    created_at = models.DateField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Долг"
        verbose_name_plural = "Долги"

    def __str__(self):
        return f"{'Наш долг' if self.is_ours else 'Долг клиента'} - {self.amount}$"



class CashTransaction(models.Model):
    WITHDRAWAL = 'withdrawal'
    INCOME = 'income'
    EXPENSE = 'expense'
    
    TYPE_CHOICES = [
        (INCOME, 'Поступление'),
        (EXPENSE, 'Расход'),
        (WITHDRAWAL, 'Изъятие средств'),
    ]
    cashbox = models.ForeignKey(CashBox, null=True, blank=True, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.PROTECT)
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="Сумма $")
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.TextField(verbose_name="Описание",blank=True)
    created_by = models.ForeignKey(User, default=1, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)        

    class Meta:
        verbose_name = "Денежная операция"
        verbose_name_plural = "Денежные операции"



 
    
# models.py

class Currency(models.Model):
    # Оставляем поле, но помечаем как неактивное
    usd_to_som = models.FloatField("Курс $ → сом (не используется)", 
                                 default=1, 
                                 editable=False)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Курс валюты"
        verbose_name_plural = "Курсы валют"

    def __str__(self):
        return "Система работает в долларах (конвертация отключена)"
