from datetime import datetime
from celery import task
from django.core.mail import EmailMultiAlternatives, get_connection
from weil.mail.models import Message, MailBoxType


@task()
def send_message(message_id):
    message = Message.objects.get(id=message_id)
    if not message:
        return

    msg = EmailMultiAlternatives(
        subject=message.subject,
        body=message.content,
        from_email=message.sender,
        to=message.to,
    )

    if message.html_content:
        msg.attach_alternative(message.html_content, "text/html")

    mailbox = message.mailbox

    if mailbox.type == MailBoxType.SMTP:
        backend = "django.core.mail.backends.smtp.EmailBackend"
        connection = get_connection(
            backend=backend,
            host=mailbox.smtp_host,
            port=int(mailbox.smtp_port),
            username=mailbox.smtp_username,
            password=mailbox.smtp_password,
            use_tls=mailbox.smtp_use_tls
        )
    elif mailbox.type == MailBoxType.SES:
        backend = "django_ses.SESBackend"
        extra = {}
        if mailbox.enable_dkim and mailbox.dkim_key:
            extra['dkim_domain'] = str(mailbox.domain)
            extra['dkim_key'] = str(mailbox.dkim_key.replace('\r', ''))

        connection = get_connection(
            backend,
            aws_access_key=mailbox.aws_access_key,
            aws_secret_key=mailbox.aws_access_secret_key, **extra)

    else:
        return

    msg.connection = connection

    msg.send(fail_silently=False)

    message.is_sent = True
    message.sent_at = datetime.now()
    message.save()


@task()
def test():
    print "Good!"
