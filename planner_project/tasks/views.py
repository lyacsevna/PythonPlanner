import json
from io import BytesIO

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from openpyxl.workbook import Workbook

from .forms import TaskCreateForm
from .models import Task, Category


def home(request):
    return render(request, 'tasks/home.html')


@login_required
def export_tasks_to_excel(request):

    tasks = Task.objects.filter(user=request.user)

    wb = Workbook()
    ws = wb.active
    ws.title = "Tasks"

    headers = ['ID', 'Title', 'Description', 'Category', 'Priority', 'Due Date']
    ws.append(headers)

    for task in tasks:
        ws.append([
            task.id,
            task.title,
            task.description,
            task.category.name if task.category else 'No Category',
            task.priority,
            task.due_date.isoformat() if task.due_date else 'No Due Date'
        ])

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="tasks.xlsx"'

    return response


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Пользователь {username} успешно зарегистрирован!')
            login(request, user)
            return redirect('task_list')
        else:
            messages.error(request, "Ошибка регистрации. Проверьте введённые данные.")
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# Вход пользователя


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('task_list')
            else:
                messages.error(request, 'Неверный логин или пароль.')
        else:
            messages.error(request, 'Пожалуйста, проверьте введённые данные.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


# Список задач для аутентифицированного пользователя

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)

    category_filter = request.GET.get('category')
    priority_filter = request.GET.get('priority')

    if category_filter:
        tasks = tasks.filter(category__name=category_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    categories = Category.objects.all()
    priorities = Task.objects.values_list('priority', flat=True).distinct()

    context = {
        'tasks': tasks,
        'categories': categories,
        'priorities': priorities,
        'request': request,
    }
    return render(request, 'tasks/task_list.html', context)


def export_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task_data = {
        'title': task.title,
        'description': task.description,
        'category_name': task.category.name if task.category else None,
        'priority': task.priority,
        'due_date': task.due_date.isoformat() if task.due_date else None,
    }

    response = HttpResponse(json.dumps(task_data), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="task_{task_id}.json"'
    return response

    response = HttpResponse(json.dumps(task_data), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="task_{task_id}.json"'
    return response


@csrf_exempt
def import_task(request):
    if request.method == 'POST':
        try:
            task_data = json.loads(request.body)
            if not isinstance(task_data, dict):
                return JsonResponse({'error': 'Ожидается объект задачи.'}, status=400)

            task_data['user'] = request.user

            # Проверяем, есть ли категория
            category_name = task_data.pop('category_name', None)
            if category_name:
                category, created = Category.objects.get_or_create(name=category_name)
                task_data['category'] = category

            form = TaskCreateForm(task_data)
            if form.is_valid():
                task = form.save()
                return JsonResponse({'message': 'Задача успешно импортирована!', 'task_id': task.id}, status=201)
            else:
                return JsonResponse({'error': form.errors}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Неверный метод'}, status=405)


@login_required
def task_create(request):
    if request.method == 'POST':
        title = request.POST.get('task_title')
        description = request.POST.get('task_description', '')
        due_date = request.POST.get('due_date') if request.POST.get('due_date') else None
        priority = request.POST.get('priority')
        category_name = request.POST.get('category')
        new_category_name = request.POST.get('new_category')

        if new_category_name:
            category, created = Category.objects.get_or_create(name=new_category_name)
        elif category_name:
            category = Category.objects.get(id=category_name)
        else:
            category = None

        Task.objects.create(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            user=request.user,
            category=category
        )

        messages.success(request, 'Задача успешно создана!')
        return redirect('task_list')

    categories = Category.objects.all()
    return render(request, 'tasks/task_create.html', {'categories': categories})


def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskCreateForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskCreateForm(instance=task)

    return render(request, 'tasks/task_form.html', {'form': form})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    messages.success(request, 'Задача успешно удалена!')
    return redirect('task_list')
