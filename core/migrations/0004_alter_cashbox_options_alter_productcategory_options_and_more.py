# Generated by Django 5.2 on 2025-04-07 15:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_cashbox_productcategory_stage_product_cashbox_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cashbox',
            options={'verbose_name': 'Касса', 'verbose_name_plural': 'Кассы'},
        ),
        migrations.AlterModelOptions(
            name='productcategory',
            options={'verbose_name': 'Категория', 'verbose_name_plural': 'Категории'},
        ),
        migrations.RemoveField(
            model_name='product',
            name='current_stage',
        ),
    ]
