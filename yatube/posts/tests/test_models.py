from django.test import TestCase

from ..models import Group, Post, User
from .conftest import ConfTests

class PostModelTest(ConfTests, TestCase):

    def test_models_have_correct_object_names(self):
        """We check that __str__ works correctly for models."""
        self.assertEqual(str(self.post), self.EXPECTED_VALUE_POST)
        self.assertEqual(str(self.group), self.TITLE_GROUP)

    def test_verbose_name(self):
        """Verbose_name field matches the expected."""
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
        """Help_text field matches the expected."""
        field_verboses = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value
                )
