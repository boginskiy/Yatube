from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Group, Post
from http import HTTPStatus


User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Nemo')
        cls.user_1 = User.objects.create_user(username='Dali')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        Post.objects.create(
            pk=22,
            text='Тестовое',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(self.user_1)

    def test_images_guest_client(self):
        """Проверка доступности страниц для любого пользователя."""
        images = [
            '/',
            '/group/test-slug/',
            '/auth/login/',
            '/auth/signup/',
            '/profile/Nemo/',
            '/posts/22/'
        ]
        for image in images:
            response = self.guest_client.get(image)
            with self.subTest(image=image):
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_images_authorized_client(self):
        """Проверка доступности страниц только для автор. пользователя."""
        images = [
            '/posts/22/edit/',
            '/posts/22/',
            '/create/'
        ]
        for image in images:
            response = self.authorized_client.get(image)
            with self.subTest(image=image):
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_html_url_posts_correct_template(self):
        """Проверка страниц по адресам url."""
        adress_html = {
            '/': 'posts/index.html',
            '/profile/Nemo/': 'posts/profile.html',
            '/posts/22/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/posts/22/': 'posts/post_detail.html'
        }
        for adress, html in adress_html.items():
            response = self.authorized_client.get(adress)
            with self.subTest(adress=adress):
                self.assertTemplateUsed(response, html)

    def test_create_list_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу login."""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_non_existent_page_url_redirect_anonymous_on_admin_login(self):
        """Страница по несуществующему адресу."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_edit_posts_author_posts(self):
        """
        Проверка доступности редактирования поста
        для автора и иного пользователя.
        """

        response = self.authorized_client.get('/posts/22/edit/?')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.authorized_client_1.get('/posts/22/edit/?')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
