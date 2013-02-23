"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth.models import User

from django.test import TestCase
from mailman.mail.models import Message, MailBox


class SimpleTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test', 'test')

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_api(self):
        self.assertTrue(self.client.login(username='test', password='test'))

        MailBox.objects.create(
            user=self.user,
            domain="example.com",
            token="token",
        )

        resp = self.client.post('/api/send', {
            'to': ['test@baye.me', 'test2@baye.me'],
            'subject': "Welcome",
            'content': "This is content",
            'html_content': "<h1>Hello</h1>",
            'token': 'token',
            'sender': 'Example<no-reply@example.com>',
        })

        print resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Message.objects.count(), 1)

