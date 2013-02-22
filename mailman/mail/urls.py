from django.conf.urls import patterns, url

urlpatterns = patterns('mailman.mail.views',
                       url(r'^api/send$', 'send', name='send'),
                       url(r'^mailbox/$', 'mailbox', name='mailbox'),
                       url(r'^mailbox/create$', 'create_mailbox', name='create_mailbox'),
                       )
