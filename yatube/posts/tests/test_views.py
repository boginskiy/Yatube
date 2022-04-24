from django.contrib.auth import get_user_model
from posts.models import Post, Group, User, Follow
from django.test import Client, TestCase
from posts.views import PAGE_COUNT
from django.urls import reverse
from http import HTTPStatus
from django import forms
from django.core.cache import cache

User = get_user_model()


class PostPagesNameSpaceTests(TestCase):
    """Проверка namespace:name у всех шаблонов всех функций."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Nemo')
        cls.group = Group.objects.create(
            title='Название тестовой группы',
            slug='slug-test',
            description='Тестовое описание группы'
        )
        cls.post = Post.objects.create(
            pk=10,
            text='Тестовая запись',
            author=cls.user,
            group=cls.group
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_url_name_coll_pagehtml_authorized_client(self):
        """Проверка namespace:name у всех шаблонов."""

        name_page = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'slug-test'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'Nemo'}):
                'posts/profile.html',
            reverse('posts:post_edit', kwargs={'post_id': 10}):
                'posts/create_post.html',
            reverse('posts:post_detail', kwargs={'post_id': 10}):
                'posts/post_detail.html',
            reverse('posts:post_create'):
                'posts/create_post.html'
        }
        for name, page in name_page.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                self.assertTemplateUsed(response, page)


class PostFunctionsTests(PostPagesNameSpaceTests):
    """
    Тестируем функции index, group_list, profile, post_detail, post_edit
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('posts:post_edit', kwargs={'post_id': cls.post.pk})

    def setUp(self):
        for x in range(13):
            Post.objects.create(text=f'text{x}',
                                author=self.user,
                                group=self.group)

    def test_get_success(self):
        """Тестируем функцию index."""

        url = reverse('posts:index')
        response = self.guest_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'posts/index.html')
        context = response.context
        page_obj = context.get('page_obj')
        self.assertEqual(len(page_obj), PAGE_COUNT)

    def test_get_success(self):
        """Тестируем функцию group_list."""

        url = reverse('posts:group_list', kwargs={'slug': self.group.slug})
        response = self.guest_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'posts/group_list.html')
        context = response.context
        group = context.get('group')
        self.assertEqual('Название тестовой группы', group.title)
        page_obj = context.get('page_obj')
        self.assertEqual(len(page_obj), PAGE_COUNT)

    def test_get_success(self):
        """Тестируем функцию profile."""

        url = reverse('posts:profile', kwargs={'username': self.user.username})
        response = self.guest_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'posts/profile.html')
        context = response.context
        author = context.get('author')
        posts_numbers = context.get('posts_numbers')
        self.assertEqual('Nemo', author.username)
        self.assertEqual(14, posts_numbers)
        page_obj = context.get('page_obj')
        self.assertEqual(len(page_obj), PAGE_COUNT)

    def test_get_success(self):
        """Тестируем функцию post_detail."""

        url = reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        response = self.guest_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'posts/post_detail.html')
        context = response.context
        post = context.get('post')
        posts_numbers = context.get('posts_numbers')
        self.assertEqual('Тестовая запись', post.text)
        self.assertEqual(14, posts_numbers)

    def test_get_success(self):
        """Тестируем функцию post_edit_1set."""

        response = self.authorized_client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'posts/create_post.html')
        form = response.context.get('form')
        self.assertEqual(form.instance, self.post)

    def test_get_auth(self):
        """Тестируем функцию post_edit_2set."""
        response = self.guest_client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_success(self):
        """Тестируем функцию post_edit_3set."""
        new_text = 'новый текст'
        data = dict(
            text=new_text
        )
        response = self.authorized_client.post(self.url, data=data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, new_text)

    def test_post_auth(self):
        """Тестируем функцию post_edit_4set."""
        response = self.guest_client.post(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_error(self):
        """Тестируем функцию post_edit_5set."""

        data = dict(
            text='new text',
        )
        response = self.authorized_client.post(self.url, data=data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)


class PostCreateTestCace_1(PostPagesNameSpaceTests):
    """Тестируем функцию post_create. Сценарий 1."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for i in range(5):
            Post.objects.create(text=f'тестовый текст № {i}',
                                author=cls.user,
                                group=cls.group)

    def test_post_in_the_right_group(self):
        """Проверяем что пост попал в свою групппу."""

        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'slug-test'}))
        self.assertEqual(len(response.context['page_obj']), 6)

    def test_post_in_the_profile(self):
        """Проверяем что пост попал в profile."""

        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Nemo'}))
        self.assertEqual(len(response.context['page_obj']), 6)


class PostCreateTestCace_2(TestCase):
    """Тестируем функцию post_create. Сценарий 2."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Nemo')
        cls.group = Group.objects.create(title='Тестовая группа1',
                                         slug='test-slug1')
        cls.post = Post.objects.create(text='тестовый текст',
                                       author=cls.user)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""

        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_get_success(self):
        """."""

        response = self.guest_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'posts/create_post.html')
        form = response.context.get('form')
        self.assertNotEqual(form.instance, self.post.text)

    def test_post_error(self):
        """."""

        data = dict(text='new text')
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_in_the_right_group(self):
        """Проверяем что пост не попал в другую группу."""

        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug1'}))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_post_in_the_major_list(self):
        """Проверяем что пост попал на главную страницу."""

        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 1)


class CasheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='Nemo')
        cls.post_cashe = Post.objects.create(
            author=cls.user,
            text='Тест кеш',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_index(self):
        """Тест кеша главной страницы."""

        response = self.authorized_client.get(
            reverse('posts:index')).content
        self.post_cashe.delete()
        response_cashe = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertEqual(response, response_cashe)
        cache.clear()
        response_clear = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(response, response_clear)


class Follow_Unfollow_Tests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_1 = User.objects.create_user(username='Admin')
        cls.user_2 = User.objects.create_user(username='Nemo')
        cls.user_3 = User.objects.create_user(username='Demo')
        cls.follow = Follow.objects.create(
            user=cls.user_2,
            author=cls.user_1,
        )
        cls.post = Post.objects.create(text='тестовый тест',
                                       author=cls.user_1)

    def setUp(self):
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)
        self.authorized_client_3 = Client()
        self.authorized_client_3.force_login(self.user_3)

    def test_follow_profile(self):
        """Пользователь подписывается на других и удаляет подписку."""

        url_profile_follow = reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_1})
        response = self.authorized_client_2.get(url_profile_follow)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Follow.objects.filter(
            user=self.user_2,
            author=self.user_1).exists())
        url_profile_unfollow = reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user_1})
        self.authorized_client_2.get(url_profile_unfollow)
        self.assertFalse(Follow.objects.filter(user=self.user_2,
                                               author=self.user_1).exists())

    def test_follow_index(self):
        """Пост появляется у тех кто подписан и нет кто не подписан."""

        response_client_2 = self.authorized_client_2.get(
            reverse('posts:follow_index'))
        self.assertEqual(len(response_client_2.context['page_obj']), 1)
        context = response_client_2.context['page_obj'][0].text
        self.assertEqual(context, 'тестовый тест')
        response_client_3 = self.authorized_client_3.get(
            reverse('posts:follow_index'))
        self.assertEqual(len(response_client_3.context['page_obj']), 0)
        self.assertEqual(response_client_3.status_code, HTTPStatus.OK)
