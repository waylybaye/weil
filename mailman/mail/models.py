from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from email.utils import parseaddr, formataddr


class MailBoxType:
    SMTP = 1
    SES = 2


MAILBOX_TYPE_CHOICES = (
    (MailBoxType.SES, 'Amazon SES'),
    (MailBoxType.SMTP, 'SMTP')
)


class MailBox(models.Model):
    user = models.ForeignKey(User, related_name="boxes")
    domain = models.CharField(max_length=100, db_index=True)
    token = models.CharField(max_length=100, db_index=True)

    type = models.SmallIntegerField(choices=MAILBOX_TYPE_CHOICES, default=1)

    aws_access_key = models.CharField(max_length=100, null=True, blank=True)
    aws_access_secret_key = models.CharField(max_length=100, null=True, blank=True)
    # DKIM settings
    enable_dkim = models.BooleanField(default=False)
    dkim_key = models.TextField(null=True, blank=True)

    smtp_host = models.CharField(max_length=255, null=True, blank=True)
    smtp_port = models.CharField(max_length=10, null=True, blank=True)
    smtp_username = models.CharField(max_length=100, null=True, blank=True)
    smtp_password = models.CharField(max_length=32, null=True, blank=True)
    smtp_use_tls = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return self.domain


class Recipient(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return formataddr((self.name, self.email))


class Message(models.Model):
    mailbox = models.ForeignKey(MailBox)

    subject = models.CharField(max_length=255)
    sender = models.CharField(max_length=100)

    recipients = models.ManyToManyField(Recipient, related_name="received_messages")
    bcc = models.ManyToManyField(Recipient)

    content = models.TextField(null=True, blank=True)
    html_content = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(default=datetime.now)

    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.subject

    @property
    def to(self):
        return [str(recipient) for recipient in self.recipients.all()]
