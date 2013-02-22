from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_POST
from mailman.mail.models import MailBox


@require_POST
def send(request):
    token = request.POST.get('token')


@login_required
def mailbox(request):
    mailboxes = MailBox.objects.filter(user=request.user)
    return render(request, 'mailbox/mailboxes.html', {'mailboxes': mailboxes})
