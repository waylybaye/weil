from celery import task
from django.core.mail import EmailMultiAlternatives, get_connection
from mailman.mail.models import Message, MailBoxType


@task()
def send_message(message_id):
    message = Message.objects.get(id=message_id)
    if not message:
        return

    print message.to

    msg = EmailMultiAlternatives(
        subject=message.subject,
        body="content",
        from_email=message.sender,
        to=message.to,
    )

    if message.html_content:
        msg.attach_alternative(message.html_content, "text/html")

    #todo: use different backend for different mailbox according config
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
        connection = get_connection(backend )
    else:
        return

    print "Backend: ", backend
    msg.connection = connection

    msg.send(fail_silently=False)


@task()
def test():
    print "Good!"
