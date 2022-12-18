from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    EXPECTED_VALUE_POST = 'a' * 15
    TITLE_GROUP = 'Teстовая группа'
    SLUG_GROUP = 'Teстовый слаг'
    DESCRIPION_GROUP = 'Тестовое описание'
    TEXT_POST = 'a' * 100

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title=cls.TITLE_GROUP,
            slug=cls.SLUG_GROUP,
            description=cls.DESCRIPION_GROUP,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=cls.TEXT_POST
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(str(self.post), self.EXPECTED_VALUE_POST)
        self.assertEqual(str(self.group), self.TITLE_GROUP)

    def test_verbose_name(self):
        """Verbose_name поля совпадает с ожидаемым."""
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(
                        field).verbose_name, expected_value)

    def test_help_text(self):
        """Help_text поля совпадает с ожидаемым."""
        field_verboses = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value
                )
