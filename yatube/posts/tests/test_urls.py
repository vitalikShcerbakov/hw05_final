from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовый текст',
        )
        cls.post = Post.objects.create(
            text='тестовый текст поля text',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        cache.clear()
        self.user = User.objects.get(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_url_exists_at_desired_location_anonymous(self):
        """Список странциц доступных любому пользователю"""
        list_url_anonymous = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user}/': HTTPStatus.OK,
            f'/posts/{self.post.pk}/': HTTPStatus.OK,
            f'/posts/{self.post.pk}/edit/': HTTPStatus.FOUND,
            '/create/': HTTPStatus.FOUND,
            '/unexisting/': HTTPStatus.NOT_FOUND,
        }
        for url, status in list_url_anonymous.items():
            with self.subTest(address=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)

    def test_home_url_exists_at_desired_location_anonymous(self):
        """Список странциц доступных авторизованному пользователю"""
        list_url_anonymous = {
            f'/posts/{self.post.pk}/edit/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            '/unexisting/': HTTPStatus.NOT_FOUND,
        }
        for url, status in list_url_anonymous.items():
            with self.subTest(address=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_urls_uses_correct_template_not_authorized(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_authorized(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_create_url_redirect_anonymous1(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.client.get('/create/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/create/'))
