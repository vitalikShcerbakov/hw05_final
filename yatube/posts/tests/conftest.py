import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ConfTests(TestCase):
    NEW_POST = 'тут текст нового поста'
    TEXT_AFTER_EDITING = 'Тут текст после редактирования'
    TITLE_GROUP = 'Teстовая группа'
    SLUG_GROUP = 'test-slug'
    DESCRIPION_GROUP = 'Тестовое описание'
    TEXT_POST = 'тестовый текст поля text'
    EXPECTED_VALUE_POST = TEXT_POST[:15]
    COUNT_POST = 13
    NEW_COMMENT = 'new comment'
    COMMENT = 'text new comment'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.name_test2 = User.objects.create_user(username='test2')
        cls.name_test1 = User.objects.create_user(username='test1')
        cls.group = Group.objects.create(
            title=cls.TITLE_GROUP,
            slug=cls.SLUG_GROUP,
            description=cls.DESCRIPION_GROUP,
        )
        cls.post = Post.objects.create(
            text=cls.TEXT_POST,
            author=cls.user,
            group=cls.group,
        )

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text=cls.COMMENT
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
