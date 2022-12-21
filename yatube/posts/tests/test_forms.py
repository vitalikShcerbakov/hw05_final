from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post

from .conftest import ConfTests


class PostCreateFormTests(ConfTests, TestCase):

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """A valid form creates a post entry."""
        post_count = Post.objects.count()
        form_data = {
            'text': self.NEW_POST,
            'group': self.group.id,
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text=self.NEW_POST).filter(
            group=self.group.id).filter(
                image='posts/small.gif').exists())

    def test_edit_post(self):
        """The valid form creates an entry in the post."""
        form_data = {
            'text': self.TEXT_AFTER_EDITING,
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertTrue(Post.objects.filter(
            id=self.post.id).filter(
                group=self.group.id).filter(
                    text=self.TEXT_AFTER_EDITING))
