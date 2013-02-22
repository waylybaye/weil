from datetime import datetime
from django.contrib.auth.models import User
from django.db import models


class MailBox(models.Model):
    user = models.ForeignKey(User, related_name="boxes")
    domain = models.CharField(max_length=100, db_index=True)
    token = models.CharField(max_length=100, db_index=True)

    # DKIM settings
    enable_dkim = models.BooleanField(default=False)
    dkim_key = models.TextField(null=True)

    created_at = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return self.domain


class Recipient(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        if self.name:
            return "%s <%s>" % (self.name, self.email)
        return self.email


class Message(models.Model):
    mailbox = models.ForeignKey(MailBox)

    subject = models.CharField(max_length=255)
    sender = models.EmailField()

    recipients = models.ManyToManyField(Recipient, related_name="received_messages")
    bcc = models.ManyToManyField(Recipient)

    content = models.TextField(null=True, blank=True)
    html_content = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(default=datetime.now)

    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.subject
