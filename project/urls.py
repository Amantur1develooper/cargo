"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from core import views
from django.contrib import admin
from django.urls import path
from django.conf import settings 
from django.urls import path
from django.conf.urls.static import static
from core.car import cargo_group_detail, cargo_group_list, export_cargo_groups_report, export_cargo_report
from core.import_kargo.views import clients_without_phone, download_example, import_products
from core.views import cashbox_detail, category_cashboxes, client_detail, client_list, dashboard, export_products_in_stock, generate_invoice, move_products_to_cashbox, product_detail, products_by_category, products_in_stock_view, return_to_warehouse, sales_report, sell_product

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',dashboard,name='dashboard'),
    path('export/products-in-stock/', export_products_in_stock, name='export_products_in_stock'),
    path('products-in-stock/', products_in_stock_view, name='products_in_stock'),
    path('invoice/', generate_invoice, name='generate-invoice'),
    path('category/<str:category_name>/', products_by_category, name='products_by_category'),

    path('products/clear-category/', views.clear_products_category, name='clear_products_category'),
    
    path('cargo/<int:cargo_group_id>/report/', export_cargo_report, name='export_cargo_report'),
    path('cargo/<int:pk>/', cargo_group_detail, name='cargo_group_detail'),
    path('cargo-groups/', cargo_group_list, name='cargo_group_list'),
    
    # path('cargo-groups/', cargo_group_list, name='cargo_group_list'),
    path('cargo-groups/export/', export_cargo_groups_report, name='export_cargo_groups'),

    
    path('sales_report/', sales_report, name='sales_report'),
    
    path('cashboxes/<str:category_name>/', category_cashboxes, name='category_cashboxes'),
    path('products/move-to-cashbox/', move_products_to_cashbox, name='move_products_to_cashbox'),

    path('reports/categories/', views.export_categories_report, name='export_categories'),
    path('reports/cashboxes/', views.export_cashboxes_report, name='export_cashboxes'),
    
    path('cashbox/<int:cashbox_id>/export/', views.export_cashbox_detail, name='export_cashbox_detail'),
    

    path('import-products/', import_products, name='import_products'),
    path('clients-without-phone/', clients_without_phone, name='clients_without_phone'),
    path('download-example/', download_example, name='download_example'),
    
path('cashbox/<int:cashbox_id>/', cashbox_detail, name='cashbox_detail'),
path('product/<int:product_id>/sell/', sell_product, name='sell_product'),
path('product/<int:product_id>/return-to-warehouse/', return_to_warehouse, name='return_to_warehouse'),


path('products/<int:pk>/', product_detail, name='product_detail'),

# urls.py
path('clients/', client_list, name='client_list'),
path('clients/<int:client_id>/', client_detail, name='client_detail'),
]



urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
