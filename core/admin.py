from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import CashBox, Client, CargoGroup, Product, FinanceOverview, Debt, CashTransaction, ProductCategory
admin.site.site_header = "Админ-панель"

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'city', 'phone')
    search_fields = ('full_name', 'city', 'phone')
    list_filter = ('city',)


@admin.register(CargoGroup)
class CargoGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle_number', 'trip_number', 'date')
    search_fields = ('vehicle_number', 'trip_number')
    list_filter = ('date',)
    date_hierarchy = 'date'



@admin.action(description="🖨️ Напечатать накладную")
def print_invoice(modeladmin, request, queryset):
    selected = queryset.values_list('pk', flat=True)
    return HttpResponseRedirect(
        reverse('generate-invoice') + f"?ids={','.join(map(str, selected))}"
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'client', 'cargo_group', 'quantity_places', 'price', 
        'total_price', 'status', 'uzb_price', 'category', 'cashbox'
    )
    search_fields = ('name', 'client__full_name', 'cargo_group__vehicle_number')
    list_filter = ('status', 'cargo_group__date', 'client__city','category', 'cashbox')
    list_editable = ('status',)
    readonly_fields = ('total_price',)
    autocomplete_fields = ('client', 'cargo_group','category', 'cashbox')
    actions = [print_invoice]  # ← Добавляем действие здесь!


@admin.register(FinanceOverview)
class FinanceOverviewAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'date', 'cash_balance', 'product_balance', 
        'debt_to_us', 'debt_ours', 'net_assets'
    )
    readonly_fields = ('net_assets',)
    list_filter = ('date',)
    date_hierarchy = 'date'


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'amount', 'is_ours', 'paid', 'created_at')
    search_fields = ('client__full_name',)
    list_filter = ('is_ours', 'paid', 'created_at')
    list_editable = ('paid',)
    date_hierarchy = 'created_at'


@admin.register(CashTransaction)
class CashTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'amount', 'description', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('description',)
    date_hierarchy = 'created_at'


# admin.p
@admin.register(CashBox)
class CashBoxAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')
    search_fields = ('name',)
    list_filter = ('category',)
    
    
@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = (
#         'id', 'name', 'quantity_kg', 'price', 'total_price',
       
#     )
#     search_fields = ('name', 'category__name', 'cashbox__name')
#     list_filter = ('category', 'cashbox')
#     readonly_fields = ('total_price',)
#     
