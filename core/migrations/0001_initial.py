# Generated by Django 5.2 on 2025-04-07 09:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CargoGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_number', models.CharField(max_length=50, verbose_name='Номер машины')),
                ('trip_number', models.CharField(max_length=50, verbose_name='Рейс')),
                ('date', models.DateField(verbose_name='Дата поставки')),
            ],
        ),
        migrations.CreateModel(
            name='CashTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('income', 'Приход'), ('expense', 'Расход')], max_length=10)),
                ('amount', models.FloatField(verbose_name='Сумма $')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255, verbose_name='ФИО')),
                ('city', models.CharField(max_length=100, verbose_name='Город')),
                ('phone', models.CharField(max_length=20, verbose_name='Телефон')),
            ],
        ),
        migrations.CreateModel(
            name='FinanceOverview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True, verbose_name='Дата')),
                ('cash_balance', models.FloatField(default=0.0, verbose_name='Остаток денег')),
                ('product_balance', models.FloatField(default=0.0, verbose_name='Товары на сумму')),
                ('debt_to_us', models.FloatField(default=0.0, verbose_name='Долги нам')),
                ('debt_ours', models.FloatField(default=0.0, verbose_name='Наши долги')),
            ],
        ),
        migrations.CreateModel(
            name='Debt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(verbose_name='Сумма долга $')),
                ('is_ours', models.BooleanField(default=False, verbose_name='Наш долг?')),
                ('created_at', models.DateField(auto_now_add=True)),
                ('paid', models.BooleanField(default=False)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='debts', to='core.client')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование товара')),
                ('packaging', models.CharField(blank=True, max_length=50, null=True, verbose_name='Упаковка')),
                ('quantity_places', models.PositiveIntegerField(default=1, verbose_name='Количество мест')),
                ('quantity_kg', models.FloatField(blank=True, null=True, verbose_name='Вес (кг)')),
                ('quantity_units', models.PositiveIntegerField(blank=True, null=True, verbose_name='Количество (шт)')),
                ('price', models.FloatField(blank=True, null=True, verbose_name='Цена за единицу ($)')),
                ('total_price', models.FloatField(blank=True, null=True, verbose_name='Сумма ($)')),
                ('transport_cost', models.FloatField(blank=True, null=True, verbose_name='Йул кира ($)')),
                ('plomb_number', models.CharField(blank=True, max_length=100, null=True, verbose_name='Пломба')),
                ('uzb_price', models.FloatField(blank=True, null=True, verbose_name='УЗБ $')),
                ('status', models.CharField(choices=[('sklad', 'На складе'), ('way', 'В пути'), ('kassa', 'На кассе'), ('sold', 'Продано')], default='sklad', max_length=10)),
                ('cargo_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='core.cargogroup')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='core.client')),
            ],
        ),
    ]
