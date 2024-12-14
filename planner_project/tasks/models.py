from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'Высокий'),
        ('medium', 'Средний'),
        ('low', 'Низкий'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return self.title
