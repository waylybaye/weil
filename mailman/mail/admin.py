from django.contrib import admin
from mailman.mail.models import MailBox, Message


admin.site.register(MailBox)
admin.site.register(Message)
