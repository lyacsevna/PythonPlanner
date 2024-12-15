from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('tasks/', views.task_list, name='task_list'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]
