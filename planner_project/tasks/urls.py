from django.urls import path
from .views import (
    home,
    register_view,
    login_view,
    task_list,
    export_task,
    import_task,
    task_create,
    task_edit,
    task_delete, export_task, import_task, export_tasks_to_excel
)

urlpatterns = [
    path('', home, name='home'),  # Главная страница
    path('register/', register_view, name='register'),  # Регистрация
    path('login/', login_view, name='login'),  # Форма входа
    path('tasks/', task_list, name='task_list'),  # Список задач
    path('task/export/<int:task_id>/', export_task, name='export_task'),  # Экспорт в json
    path('task/import/', import_task, name='import_task'),  # Импорт из json
    path('tasks/create/', task_create, name='task_create'),  # Создание задачи
    path('tasks/edit/<int:pk>/', task_edit, name='task_form'),  # Редактирование задачи
    path('tasks/delete/<int:pk>/', task_delete, name='task_delete'),  # Удаление задачи
    path('export_tasks/', export_tasks_to_excel, name='export_tasks'),  # Экспорт в Excel
]
