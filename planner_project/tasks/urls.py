from django.urls import path
from .views import home, task_list
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', home, name='home'),
    path('tasks/', task_list, name='task_list'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]
