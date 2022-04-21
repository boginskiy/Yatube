from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus


User = get_user_model()


class UserURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Nemo')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_url_exists_at_desired_location_guest_client(self):
        """Проверка доступности адресов users."""
        url_users = [
            '/auth/signup/',
            '/auth/login/',
            '/auth/password_reset/',
        ]
        for url in url_users:
            response = self.guest_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_url_exists_at_desired_location_authorized_client(self):
        """Проверка доступности адресов users для
        зарегистрированного пользователя."""
        url_users = [
            '/auth/password_change/',
            '/auth/logout/',
        ]
        for url in url_users:
            response = self.authorized_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_html_url_users_correct_template(self):
        """Проверка страниц по адресам url."""
        adress_html = {
            '/auth/password_reset/': 'users/password_reset_form.html',
        }
        for adress, html in adress_html.items():
            response = self.authorized_client.get(adress)
            with self.subTest(adress=adress):
                self.assertTemplateUsed(response, html)
