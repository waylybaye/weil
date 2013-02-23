from email.utils import parseaddr
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from mailman.mail.models import MailBox, Message, Recipient
from mailman.mail.tasks import send_message


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


@login_required
def mailbox(request):
    mailboxes = MailBox.objects.filter(user=request.user)
    return render(request, 'mailbox/mailboxes.html', {'mailboxes': mailboxes})
