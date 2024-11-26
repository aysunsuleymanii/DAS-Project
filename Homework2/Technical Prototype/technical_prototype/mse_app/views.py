from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import os

from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages


def create_account(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        email = request.POST['email']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken')
            return redirect('create_account')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('create_account')

        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()

        messages.success(request, 'Account created successfully!')
        return redirect('dashboard')
    return render(request, 'create_account.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'dashboard.html', {'user': request.user})


def report_analysis(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'report_analysis.html', {'user': request.user})


def user_logout(request):
    logout(request)
    return redirect('login')


def process_excel(file_path, selected_companies, start_date, end_date):
    data = pd.read_excel(file_path)

    data['date'] = pd.to_datetime(data['date'], errors='coerce')
    data['last_trade_price'] = data['last_trade_price'].replace({',': ''}, regex=True)
    data['last_trade_price'] = pd.to_numeric(data['last_trade_price'], errors='coerce')
    data = data.set_index("company_name")

    filtered_data = data[
        (data.index.isin(selected_companies)) & (data['date'] >= start_date) & (data['date'] <= end_date)
        ]

    if filtered_data.empty:
        return None

    fig, ax = plt.subplots()
    for company in selected_companies:
        company_data = filtered_data[filtered_data.index == company]
        ax.plot(company_data['date'], company_data['last_trade_price'], label=company)

    ax.set_xlabel('Date')
    ax.set_ylabel('Last Trade Price')
    ax.legend()
    ax.set_title('Stock Prices')

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return img_str


def stock_chart_view(request):
    file_path = os.path.join(
        "/Users/aysunsuleymanturk/Desktop/Software Arch and Design/SDA-Project/Homework1/",
        "stock_data.xlsx"
    )
    selected_companies = request.GET.getlist('companies', [])
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not selected_companies or not start_date or not end_date:
        return JsonResponse({'success': False, 'error': 'Invalid input parameters'})

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    img_str = process_excel(file_path, selected_companies, start_date, end_date)

    if not img_str:
        return JsonResponse({'success': False, 'error': 'No data available for the selected criteria'})

    return JsonResponse({'success': True, 'image': img_str})


def get_stock_data(request):
    if request.method == 'GET':
        try:
            selected_company = request.GET.get('company', None)

            if not selected_company:
                return JsonResponse({'success': False, 'error': 'No company specified'}, status=400)

            file_path = "/Users/aysunsuleymanturk/Desktop/Software Arch and Design/SDA-Project/Homework1/stock_data.xlsx"

            data = pd.read_excel(file_path)

            data['date'] = pd.to_datetime(data['date'], errors='coerce')

            # Clean 'last_trade_price' by removing commas and converting to float
            data['last_trade_price'] = data['last_trade_price'].replace({',': ''}, regex=True)
            data['last_trade_price'] = pd.to_numeric(data['last_trade_price'], errors='coerce')

            company_data = data[data['company_name'] == selected_company]

            if company_data.empty:
                return JsonResponse({'success': False, 'error': 'No data found for the selected company'}, status=404)

            response_data = company_data[['date', 'last_trade_price']].dropna().to_dict(orient='records')

            return JsonResponse({'success': True, 'data': response_data}, status=200)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
