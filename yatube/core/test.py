from django.test import TestCase


class CastomPageURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_urls_uses_correct_template(self):
        """The URL uses the appropriate pattern."""
        response = self.client.get('unexisting')
        self.assertTemplateUsed(response, 'core/404.html')
