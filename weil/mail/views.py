# coding: utf-8
from email.utils import parseaddr
from django.core.mail import send_mail
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from weil.mail.models import MailBox, Message, Recipient
from weil.mail.tasks import send_message


class HttpBadRequest(HttpResponse):
    status_code = 400


@csrf_exempt
@require_POST
def send(request):
    token = request.POST.get('token')
    to = request.POST.getlist('to')
    subject = request.POST.get('subject')
    content = request.POST.get('content')
    html_content = request.POST.get('html_content')
    sender = request.POST.get('sender')

    required_params = ['subject', 'content', 'sender']
    for param in required_params:
        if not request.POST.get(param):
            return HttpBadRequest("%s is required." % param)

    if not to:
        return HttpBadRequest("Recipients address missing.")

    if not '@' in sender:
        return HttpBadRequest("Invalid sender address.")

    sender_name, sender_email = parseaddr(sender)
    domain = sender_email.split('@')[1]

    try:
        mailbox = MailBox.objects.get(domain=domain)
        if not mailbox.token == token:
            return HttpBadRequest("Invalid token.")

        message = Message.objects.create(
            mailbox=mailbox,
            subject=subject,
            content=content,
            html_content=html_content,
            sender=sender,
        )

        for recipient in to:
            name, addr = parseaddr(recipient)
            instance, created = Recipient.objects.get_or_create(name=name, email=addr)
            message.recipients.add(instance)

        send_message.delay(message.id)
        return HttpResponse()

    except MailBox.DoesNotExist:
        return HttpBadRequest("Unverified sender address.")


def test(request):
    send_mail(u"测试SES", u"测试中文邮件", '尺乎 <no-reply@chehu.net>', ['Baye <havelove@gmail.com>'])
    return HttpResponse("OK")
