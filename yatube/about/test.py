from django.test import Client, TestCase


class StiticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location_author(self):
        """Проверка доступности адреса /about/author"""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_about_url_exists_at_desired_location_tech(self):
        """Проверка доступности адреса /about/tech"""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_about_url_uses_correct_template_author(self):
        """Проверка шаблона для адреса /about/author"""
        response = self.guest_client.get('/about/author/')
        self.assertTemplateUsed(response, 'about/author.html')

    def test_about_url_uses_correct_template_tech(self):
        """Проверка шаблона для адреса /about/tech"""
        response = self.guest_client.get('/about/tech/')
        self.assertTemplateUsed(response, 'about/tech.html')
