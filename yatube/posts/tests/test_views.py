import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post

User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    COUNT_POST = 20

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Guido')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовый текст',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.list_post = [Post.objects.create(
            text='тестовый текст поля text',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )for _ in range(cls.COUNT_POST)]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.expected_post_list = list(
            Post.objects.all()[:settings.AMOUNT_OF_POSTS_TO_DISPLAY])
        self.user = User.objects.get(username='Guido')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post = self.list_post[0]
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post.pk}): 'posts/post_detail.html',
            reverse(
                'posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': post.pk}): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def reconciliation_of_posts_by_fields(self, obj_list):
        for pst, post in zip(obj_list, self.list_post[::-1]):
            self.assertEqual(pst.id, post.id)
            self.assertEqual(pst.author.id, post.author.id)
            self.assertEqual(pst.group.id, post.group.id)
            self.assertEqual(pst.author.username, post.author.username)
            self.assertEqual(pst.text, post.text)
            self.assertEqual(pst.group.title, post.group.title)
            self.assertEqual(type(pst), type(post))
            self.assertEqual(pst.image.size, post.image.size)
            self.assertEqual(pst.image, post.image)

    def test_displaying_posts_from_the_main_page(self):
        """Проверяет, что шаблон index содержит список постов."""
        response = self.authorized_client.get(reverse('posts:index'))
        obj_list = response.context['page_obj']
        self.reconciliation_of_posts_by_fields(obj_list)
        self.assertEqual(list(obj_list), self.expected_post_list)

    def test_output_of_posts_filtered_by_group(self):
        """Проверяет, что шаблон group_list содержит список постов."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': f'{self.group.slug}'}))
        obj_list = response.context['page_obj']
        self.reconciliation_of_posts_by_fields(obj_list)
        self.assertEqual(list(obj_list), self.expected_post_list)

    def test_displaying_posts_filtered_by_user(self):
        """Проверяет, что шаблон profile содержит список постов."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user}))
        obj_list = response.context['page_obj']
        self.reconciliation_of_posts_by_fields(obj_list)
        self.assertEqual(list(obj_list), self.expected_post_list)

    def test_output_of_one_post_filtered_by_id(self):
        """Проверяет, что шаблон post_detail содержит пост."""
        one_post_id = self.list_post[0].id
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': one_post_id}))
        one_post = response.context['one_post']
        expected_post = Post.objects.get(id=one_post_id)
        self.assertEqual(one_post, expected_post)
        self.assertEqual(one_post.id, expected_post.id)
        self.assertEqual(one_post.image, expected_post.image)

    def _test_forms(self, response):
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,

        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context_filtered_by_id(self):
        """Проверяет, что шаблон post_edit cодержит форму."""
        one_post_id = self.list_post[0].id
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': one_post_id})
        )
        self._test_forms(response)

    def test_create_post_single_post(self):
        """Проверяет, что шаблон create_post cодержит форму."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self._test_forms(response)

    def test_cache_on_index_page(self):
        response = self.authorized_client.get(reverse('posts:index'))
        before_content = response.content
        Post.objects.all().delete()
        response_after_removal = self.authorized_client.get(
            reverse('posts:index'))
        after_removal_obj = response_after_removal.content
        self.assertEqual(before_content, after_removal_obj)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        after_deleting_cache = response.content
        self.assertNotEqual(before_content, after_deleting_cache)


class PaginatorViewsTest(TestCase):
    COUNT_POST = 13

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Guido')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовый текст',
        )
        for i in range(cls.COUNT_POST):
            Post.objects.create(
                text='тестовый текст поля text',
                author=cls.user,
                group=cls.group,
            )

    def setUp(self):
        cache.clear()
        self.user = User.objects.get(username='Guido')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_contains_records(self):
        templates_pages_names = {
            'posts:index': None,
            'posts:group_list': {'slug': f'{self.group.slug}'},
            'posts:profile': {'username': f'{self.user}'},
        }
        for template_name, kwargs in templates_pages_names.items():
            response = self.authorized_client.get(reverse(
                template_name, kwargs=kwargs))
            self.assertEqual(
                len(response.context['page_obj']),
                settings.AMOUNT_OF_POSTS_TO_DISPLAY)

        for template_name, kwargs in templates_pages_names.items():
            response = self.authorized_client.get(reverse(
                template_name, kwargs=kwargs) + '?page=2')
            self.assertEqual(
                len(response.context['page_obj']),
                self.COUNT_POST - settings.AMOUNT_OF_POSTS_TO_DISPLAY)


class CommentsTest(TestCase):
    new_comment = 'new comment'
    comment = 'text new comment'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Guido')
        cls.post = Post.objects.create(
            text='текст для теста',
            author=cls.user
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text=cls.comment
        )

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_only_authorized_users_can_commen_o_posts(self):
        count_comment = Comment.objects.all().count()
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data={'text': self.new_comment}
        )
        self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data={'text': self.new_comment}
        )
        self.assertEqual(Comment.objects.count(), count_comment + 1)
        self.assertTrue(Comment.objects.filter(text=self.new_comment).exists())

    def test_comment_appears_on_post_page(self):
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data={'text': self.new_comment}
        )
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        obj_comment = response.context['comments'][1]
        expected_comment = Comment.objects.get(text=self.new_comment)
        self.assertEqual(obj_comment.id, expected_comment.id)
        self.assertEqual(obj_comment.text, expected_comment.text)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='Guido')
        cls.Noname_user = User.objects.create_user(username='Noname')
        cls.test = User.objects.create_user(username='test1')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовый текст',
        )
        Post.objects.create(
            text='тестовый текст поля text',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.not_signed = Client()
        self.not_signed.force_login(self.test)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.Noname_user)
        self.guido = Client()
        self.guido.force_login(self.user)
        self.not_authorized = Client()

    def test_authorized_client_subscribe(self):
        """Авторизованный пользователь может подписываться на других
        пользователей и удалять их из подписок"""
        number_of_subscriptions = Follow.objects.count()
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.user})
        )
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.Noname_user})
        )
        self.not_authorized.get(
            reverse('posts:profile_follow', kwargs={'username': self.user})
        )
        self.assertEqual(Follow.objects.count(), number_of_subscriptions + 1)
        self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': self.user})
        )
        self.assertEqual(Follow.objects.count(), number_of_subscriptions)

    def test_new_entry_appears(self):
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.user})
        )
        response_before_signed = self.authorized_client.get(
            reverse('posts:follow_index'))
        response_before_not_signed = self.not_signed.get(
            reverse('posts:follow_index'))
        form_data = {
            'text': 'Текст нового поста',
        }
        self.guido.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        response_signed = self.authorized_client.get(
            reverse('posts:follow_index'))
        response_not_signed = self.not_signed.get(
            reverse('posts:follow_index'))
        self.assertNotEqual(
            response_signed.content,
            response_before_signed.content
        )
        self.assertEqual(
            response_not_signed.content, response_before_not_signed.content)
