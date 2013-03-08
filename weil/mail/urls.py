from django.conf.urls import patterns, url

urlpatterns = patterns(
    'weil.mail.views',
    url(r'^test$', 'test', name='test'),
    url(r'^api/send$', 'send', name='send'),
)
