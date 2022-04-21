from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.contrib.auth import get_user_model
from posts.models import Post, Group, Comment
from posts.forms import PostForm, CommentForm
from django.conf import settings
from django.urls import reverse
from http import HTTPStatus
from django import forms
import tempfile
import shutil


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    """Проверка создания записи в бд поста с картинкой"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Nemo')
        cls.group = Group.objects.create(slug='slug-test')
        small_gif_2 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif_2',
            content=small_gif_2,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            pk=10,
            text='Тестовая запись',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )
        cls.form = PostForm()
        cls.form = CommentForm()
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""

        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тест запись',
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)

        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': self.user}))

        self.assertTrue(
            Post.objects.filter(
                text='Тест запись',
                group=self.group.pk,
                image='posts/small.gif'
            ).exists()
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_success_post(self):
        """Проверка внесения правок в пост."""

        new_text = 'новый текст'
        data = dict(text=new_text)
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}),
            data=data
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, new_text)

    def test_home_page_show_correct_context_xxxx(self):
        """Шаблон create_post сформирован с правильным контекстом для image."""

        response = self.authorized_client.get(reverse('posts:post_create'))
        form_field = response.context['form'].fields['image']
        self.assertIsInstance(form_field, forms.ImageField)

    def test_home_page_show_correct_context(self):
        """
        Проверка передачи через context поста с image
        для index, profile, group_list.
        """

        array_of_pages = [
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': 'Nemo'}),
            reverse('posts:group_list', kwargs={'slug': 'slug-test'}),
        ]
        for post in array_of_pages:
            response = self.authorized_client.get(post)
            for post in response.context['page_obj'].object_list:
                self.assertEqual(post.image, 'posts/small.gif_2')

    def test_home_page_show_correct_context(self):
        """Проверка передачи через context поста с image для post_detail."""

        url = reverse('posts:post_detail', kwargs={'post_id': 10})
        response = self.authorized_client.get(url)
        context = response.context['post'].image
        self.assertEqual(context, 'posts/small.gif_2')


class CommentFormTests(PostFormTests):
    """Тестирование комментов"""

    def test_guest_client_not_add_comment(self):
        """Комментарии делает только авторизованный пользователь."""

        url = reverse('posts:add_comment', kwargs={'post_id': self.post.pk})
        response = self.guest_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_authorized_client_add_comment(self):
        """."""

        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тест-комментарий',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': 10}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs={'post_id': 10}))
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(Comment.objects.filter(
            text='Тест-комментарий').exists())

        response_get = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': 10}))
        context = response_get.context['comments'][0].text
        self.assertEqual(context, 'Тест-комментарий')
