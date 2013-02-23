"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth.models import User
from django.core.management import call_command

from django.test import TestCase
from django.core import mail
from mailman.mail.models import Message, MailBox


class MailTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test', 'test')
        self.mailbox = MailBox.objects.create(
            user=self.user,
            domain="example.com",
            token="token",
        )

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_api(self):
        self.assertTrue(self.client.login(username='test', password='test'))


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

    def test_sendmail(self):
        self.assertEqual(len(mail.outbox), 0)

        Message.objects.create(
            mailbox=self.mailbox,
            subject="Hello",
            content="content",
            html_content="<h1>content</h1>"
        )
        call_command("sendmail")
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
