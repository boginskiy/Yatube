from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Group, Post


User = get_user_model()


class PostModelTest(TestCase):
    """Класс для тестирования модели Post."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create()
        cls.post = Post.objects.create(
            author=cls.user,
            text='long text long text long text long text long text long text'
        )

    def test_str(self):
        """Тест для отображения модели [:15]."""
        post = PostModelTest.post
        result = str(post)
        self.assertEqual(result, post.text[:15])


class GroupModelTest(TestCase):
    """Класс для тестирования модели Group."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Группа поклонников тестов',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )

    def test_name_group(self):
        """Тест названия группы."""
        group = GroupModelTest.group
        result = group.title
        self.assertEqual(result, 'Группа поклонников тестов')

    def test_str_text(self):
        """Отображение поля __str__ в модели."""
        group = GroupModelTest.group
        result = str(group)
        self.assertEqual(result, 'Группа поклонников тестов')

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Адрес группы на сайте',
            'description': 'Описание группы'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_help_text = {
            'title': 'максимум 200 символов',
            'slug': 'Указать адрес, используя только латиницу, '
            'цифры, дефис и знак подчеркивания',
            'description': 'Указать краткое наименование кумира и его '
            'профессиональную сферу деятельности'
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value
                )
