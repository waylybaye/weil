from celery import task
from django.core.mail import EmailMultiAlternatives, get_connection
from mailman.mail.models import Message


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
    connection = get_connection()
    msg.connection = connection

    msg.send(fail_silently=False)


@task()
def test():
    print "Good!"
