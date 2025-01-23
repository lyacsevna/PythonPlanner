from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class RegistrationTests(TestCase):
    def setUp(self):
        self.url = reverse('register')

    def test_registration_page_status_code(self):
        """Тестируем, что страница регистрации доступна (код состояния 200)."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_registration_page_template(self):
        """Проверяем, что используется правильный шаблон для страницы регистрации."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'register.html')  # Указываем имя шаблона

    def test_successful_registration(self):
        """Тестируем успешную регистрацию пользователя."""
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
        })
        self.assertEqual(response.status_code, 302)  # Ожидаем перенаправление
        self.assertTrue(User.objects.filter(username='testuser').exists())  # Проверяем, что пользователь создан

    def test_registration_with_existing_username(self):
        """Тестируем регистрацию с уже существующим именем пользователя."""
        User.objects.create_user(username='testuser', password='TestPassword123')
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123'})
        self.assertEqual(response.status_code, 200)  # Ожидаем, что форма будет повторно отображена
        self.assertFormError(response, 'form', 'username', 'Пользователь с таким именем уже существует.')

    def test_registration_with_mismatched_passwords(self):
        """Тестируем регистрацию с несовпадающими паролями."""
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password1': 'TestPassword123',
            'password2': 'DifferentPassword123'})
        self.assertEqual(response.status_code, 200)  # Ожидаем, что форма будет повторно отображена
        self.assertFormError(response, 'form', 'password2', 'Пароли не совпадают.')

    def test_registration_with_missing_fields(self):
        """Тестируем регистрацию с отсутствующими обязательными полями."""
        response = self.client.post(self.url, {
            'username': '',
            'password1': '',
            'password2': '', })
        self.assertEqual(response.status_code, 200)  # Ожидаем, что форма будет повторно отображена
        self.assertFormError(response, 'form', 'username', 'Это поле обязательно.')
        self.assertFormError(response, 'form', 'password1', 'Это поле обязательно.')
        self.assertFormError(response, 'form', 'password2', 'Это поле обязательно.')
