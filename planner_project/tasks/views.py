from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Task

def home(request):
    if request.method == 'POST':
        if 'register' in request.POST:
            return register(request)
        elif 'login' in request.POST:
            return login_view(request)
    return render(request, 'tasks/home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Пользователь {username} успешно зарегистрирован!')
            login(request, user)  # Автоматически авторизуем пользователя после регистрации
            return redirect('task_list')  # Перенаправление на список задач
    else:
        form = UserCreationForm()
    return render(request, 'tasks/home.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('task_list')  # Перенаправление на список задач
        else:
            messages.error(request, 'Неверный логин или пароль.')
    return render(request, 'tasks/home.html')  # Если не удалось авторизоваться, возвращаем на главную

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

def export_tasks(request):
    if request.method == 'GET':
        tasks = Task.objects.filter(user=request.user).values()
        return JsonResponse(list(tasks), safe=False)

@csrf_exempt
def import_tasks(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        for item in data:
            task = Task(
                title=item['title'],
                description=item['description'],
                due_date=item['due_date'],
                priority=item['priority'],
                user=request.user,
                category_id=item.get('category_id')  # если категория передается
            )
            task.save()
        return JsonResponse({'status': 'success'}, status=201)

# @login_required
# def task_list(request):
#     tasks = Task.objects.filter(user=request.user)
#     return render(request, 'tasks/task_list.html', {'tasks': tasks})
#
#
# @login_required
# def task_create(request):
#     if request.method == 'POST':
#         form = TaskForm(request.POST)
#         if form.is_valid():
#             task = form.save(commit=False)
#             task.user = request.user
#             task.save()
#             messages.success(request, 'Задача успешно создана!')
#             return redirect('task_list')
#     else:
#         form = TaskForm()
#     return render(request, 'tasks/task_form.html', {'form': form})
#
#
# @login_required
# def task_edit(request, pk):
#     task = Task.objects.get(pk=pk)
#     if request.method == 'POST':
#         form = TaskForm(request.POST, instance=task)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Задача успешно обновлена!')
#             return redirect('task_list')
#     else:
#         form = TaskForm(instance=task)
#     return render(request, 'tasks/task_form.html', {'form': form})
#
#
# @login_required
# def task_delete(request, pk):
#     task = Task.objects.get(pk=pk)
#     task.delete()
#     messages.success(request, 'Задача успешно удалена!')
#     return redirect('task_list')
#
#
# def home(request):
#     return render(request, 'tasks/home.html')  # Измените на 'tasks/home.html'
