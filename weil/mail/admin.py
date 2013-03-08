from django.contrib import admin
from mailman.mail.models import MailBox, Message


class MailBoxAdmin(admin.ModelAdmin):
    list_display = ["user", "domain", "type"]

class MessageAdmin(admin.ModelAdmin):
    list_display = ["subject", "mailbox", "is_sent", "sent_at"]

admin.site.register(MailBox, MailBoxAdmin)
admin.site.register(Message, MessageAdmin)
