from django.test import TestCase, Client


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адреса /about/.../."""

        url_about = ['/about/author/', '/about/tech/']
        for url in url_about:
            response = self.guest_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(response.status_code, 200)
