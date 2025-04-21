from datetime import datetime
from django.shortcuts import redirect, render
import pandas as pd
from django.db import transaction
from django.contrib import messages
from core.forms import ImportProductsForm
from core.models import CargoGroup, Client, Product
from django.http import HttpResponse
from openpyxl import Workbook

def download_example(request):
    wb = Workbook()
    ws = wb.active
    
    # Заголовки
    headers = ["ФИО", "Телефон", "Город", "Товар", "Вес", "Цена"]
    ws.append(headers)
    
    # Пример данных
    example_data = [
        ["Иванов Иван", "+77771234567", "Алматы", "Яблоки", 100, 1.5],
        ["Петров Петр", "+77776543210", "Нур-Султан", "Груши", 150, 2.0],
    ]
    
    for row in example_data:
        ws.append(row)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="import_example.xlsx"'
    wb.save(response)
    
    return response


import pandas as pd
import re
from django.db import transaction
from django.contrib import messages

def import_products(request):
    if request.method == 'POST':
        form = ImportProductsForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                excel_file = form.cleaned_data['excel_file']
                
                # Читаем все листы Excel
                xls = pd.ExcelFile(excel_file)
                
                # Обрабатываем основной лист (первый лист)
                df = pd.read_excel(excel_file, sheet_name=0, header=2)  # Пропускаем 2 строки заголовка
                
                # Удаляем пустые строки
                df = df.dropna(how='all')
                
                # Извлекаем информацию о рейсе из первой строки
                first_row = pd.read_excel(excel_file, sheet_name=0, nrows=1, header=None)
                trip_info = first_row.iloc[0, 0]
                
                # Парсим информацию о рейсе
                date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', trip_info)
                vehicle_match = re.search(r'(\w{2}\s?\w{3,4}\s?\w{2,4})', trip_info)
                trip_number_match = re.search(r'(\d+)-рейс', trip_info)
                
                date = date_match.group(1) if date_match else datetime.now().date()
                vehicle_number = vehicle_match.group(1) if vehicle_match else 'Не указано'
                trip_number = trip_number_match.group(1) if trip_number_match else '001'
                
                # Нормализация данных
                df.columns = ['№', 'ФИО', 'Город', 'г/п', 'Телефон', 'Наименование', 'Место', 
                             'Упак', 'шт', 'кг', 'Цена $', 'Сумма $', 'Йул кира $', 'Пломба', 'УЗБ $']
                
                # Очистка данных
                df = df[df['ФИО'].notna()]  # Удаляем строки без ФИО
                df['Телефон'] = df['Телефон'].fillna('').astype(str).str.strip()
                df['Город'] = df['Город'].fillna('').astype(str).str.strip()
                
                # Обработка числовых полей
                numeric_cols = ['кг', 'Цена $', 'Сумма $', 'Йул кира $', 'УЗБ $']
                for col in numeric_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
                with transaction.atomic():
                    # Создаем грузовую группу
                    cargo_group, created = CargoGroup.objects.get_or_create(
                        trip_number=trip_number,
                        defaults={
                            'vehicle_number': vehicle_number,
                            'date': datetime.strptime(date, '%d.%m.%Y').date() if isinstance(date, str) else date
                        }
                    )
                    
                    clients_without_phone = []
                    imported_products = 0
                    
                    for _, row in df.iterrows():
                        try:
                            phone = str(row['Телефон']).strip()
                            full_name = str(row['ФИО']).strip()
                            
                            if not full_name:
                                continue
                            
                            # Обработка клиента
                            if phone and phone != 'nan':
                                client, _ = Client.objects.get_or_create(
                                    phone=phone,
                                    defaults={
                                        'full_name': full_name,
                                        'city': row['Город'],
                                        'no_phone': False
                                    }
                                )
                            else:
                                # Ищем клиента только по ФИО и городу, если нет телефона
                                client, created = Client.objects.get_or_create(
                                    full_name=full_name,
                                    city=row['Город'],
                                    phone=None,
                                    defaults={'no_phone': True}
                                )
                                if created:
                                    clients_without_phone.append(client)
                            
                            # Обработка веса (может содержать формулы типа "=82+93")
                            weight = row['кг']
                            if isinstance(weight, str) and '=' in weight:
                                try:
                                    weight = eval(weight.replace('=', '').replace('+', ' ').split()[0])
                                except:
                                    weight = 0
                            
                            # Обработка транспортных расходов (может содержать формулы типа "=30000/12800")
                            transport_cost = row['Йул кира $']
                            if isinstance(transport_cost, str) and '=' in transport_cost:
                                try:
                                    transport_cost = eval(transport_cost.replace('=', ''))
                                except:
                                    transport_cost = 0
                            
                            # Создаем товар
                            Product.objects.create(
                                cargo_group=cargo_group,
                                client=client,
                                name=row['Наименование'],
                                packaging=row['Упак'],
                                quantity_places=row['шт'] if pd.notna(row['шт']) else 1,
                                quantity_kg=weight,
                                price=row['Цена $'],
                                total_price=row['Сумма $'] if row['Сумма $'] else weight * row['Цена $'],
                                transport_cost=transport_cost,
                                plomb_number=row['Пломба'] if pd.notna(row['Пломба']) else '',
                                uzb_price=row['УЗБ $']
                            )
                            imported_products += 1
                            
                        except Exception as e:
                            messages.warning(request, f"Ошибка обработки строки {row['№']}: {str(e)}")
                            continue
                    
                    messages.success(request, f"Успешно импортировано {imported_products} товаров в рейс {trip_number}")
                    
                    if clients_without_phone:
                        request.session['clients_without_phone'] = [
                            {'id': c.id, 'name': c.full_name, 'city': c.city} 
                            for c in clients_without_phone
                        ]
                        return redirect('clients_without_phone')
                    
                    return redirect('cargo_group_detail', pk=cargo_group.id)
                    
            except Exception as e:
                messages.error(request, f"Ошибка импорта: {str(e)}")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме")
    else:
        form = ImportProductsForm()
    
    return render(request, 'import_products.html', {'form': form})

from django.shortcuts import render
from core.models import Client

def clients_without_phone(request):
    if 'clients_without_phone' not in request.session:
        return redirect('import_products')
    
    clients_data = request.session['clients_without_phone']
    clients = Client.objects.filter(id__in=[c['id'] for c in clients_data])
    
    if request.method == 'POST':
        for client in clients:
            phone = request.POST.get(f'phone_{client.id}', '').strip()
            if phone:
                client.phone = phone
                client.no_phone = False
                client.save()
        
        del request.session['clients_without_phone']
        messages.success(request, "Телефоны клиентов успешно обновлены!")
        return redirect('cargo_group_list')
    
    return render(request, 'clients_without_phone.html', {'clients': clients})