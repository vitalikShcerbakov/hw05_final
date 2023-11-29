from django import forms
from django.conf import settings
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Follow, Post, User

from .conftest import ConfTests


class PostsPagesTests(ConfTests, TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.list_post = [Post.objects.create(
            text=cls.TEXT_POST,
            author=cls.user,
            group=cls.group,
            image=cls.uploaded
        )for _ in range(cls.COUNT_POST)]

    def setUp(self):
        cache.clear()
        self.expected_post_list = list(
            Post.objects.all()[:settings.AMOUNT_OF_POSTS_TO_DISPLAY])
        self.user = User.objects.get(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """The URL uses the appropriate pattern."""
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
        """Checks that the index template contains a list of posts."""
        response = self.authorized_client.get(reverse('posts:index'))
        obj_list = response.context['page_obj']
        self.reconciliation_of_posts_by_fields(obj_list)
        self.assertEqual(list(obj_list), self.expected_post_list)

    def test_output_of_posts_filtered_by_group(self):
        """Checks that the group_lsit template contains a list of posts."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': f'{self.group.slug}'}))
        obj_list = response.context['page_obj']
        self.reconciliation_of_posts_by_fields(obj_list)
        self.assertEqual(list(obj_list), self.expected_post_list)

    def test_displaying_posts_filtered_by_user(self):
        """Checks that the profile template contains a list of posts."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user}))
        obj_list = response.context['page_obj']
        self.reconciliation_of_posts_by_fields(obj_list)
        self.assertEqual(list(obj_list), self.expected_post_list)

    def test_output_of_one_post_filtered_by_id(self):
        """Checks that the post_detail template contains a list of posts."""
        one_post_id = self.list_post[0].id
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': one_post_id}))
        one_post = response.context['one_post']
        expected_post = Post.objects.get(id=one_post_id)
        self.assertEqual(one_post, expected_post)
        self.assertEqual(one_post.id, expected_post.id)
        self.assertEqual(one_post.image, expected_post.image)
        breakpoint()
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
        """Checks that the post_edit template contains a form."""
        one_post_id = self.list_post[0].id
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': one_post_id})
        )
        self._test_forms(response)

    def test_create_post_single_post(self):
        """Checks that the creat_post template contains a form.."""
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


class PaginatorViewsTest(ConfTests, TestCase):

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.name_test1)

    def test_contains_records(self):
        for _ in range(self.COUNT_POST):
            Post.objects.create(
                text=self.TEXT_POST,
                author=self.user,
                group=self.group,
            )
        count_post = Post.objects.all().count()
        # Subscribe to the author to check the paginator
        self.authorized_client_2.get(
            reverse('posts:profile_follow', kwargs={'username': self.user})
        )
        templates_pages_names = {
            'posts:index': None,
            'posts:follow_index': None,
            'posts:group_list': {'slug': f'{self.group.slug}'},
            'posts:profile': {'username': f'{self.user}'},
        }
        pages_and_number_of_posts = {
            '': settings.AMOUNT_OF_POSTS_TO_DISPLAY,
            '?page=2': count_post - settings.AMOUNT_OF_POSTS_TO_DISPLAY
        }
        for template_name, kwargs in templates_pages_names.items():
            for url, number in pages_and_number_of_posts.items():
                response = self.authorized_client_2.get(reverse(
                    template_name, kwargs=kwargs) + url)
                self.assertEqual(
                    len(response.context['page_obj']), number)


class CommentsTest(ConfTests, TestCase):

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_only_authorized_users_can_commen_o_posts(self):
        count_comment = Comment.objects.all().count()
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data={'text': self.NEW_COMMENT}
        )
        self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data={'text': self.NEW_COMMENT}
        )
        self.assertEqual(Comment.objects.count(), count_comment + 1)
        self.assertTrue(Comment.objects.filter(text=self.NEW_COMMENT).exists())

    def test_comment_appears_on_post_page(self):
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data={'text': self.NEW_COMMENT}
        )
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        obj_comment = response.context['comments'][1]
        expected_comment = Comment.objects.get(text=self.NEW_COMMENT)
        self.assertEqual(obj_comment.id, expected_comment.id)
        self.assertEqual(obj_comment.text, expected_comment.text)


class FollowTest(ConfTests, TestCase):

    def setUp(self):
        self.not_signed = Client()
        self.not_signed.force_login(self.name_test1)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.name_test2)
        self.guido = Client()
        self.guido.force_login(self.user)
        self.not_authorized = Client()

    def test_authorized_client_subscribe(self):
        """An authorized user can follow others
         users and remove them from subscriptions"""
        number_of_subscriptions = Follow.objects.count()
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.user})
        )
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.name_test2})
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
            'text': self.TEXT_POST,
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
