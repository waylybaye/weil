from django.views.decorators.http import require_POST


@require_POST
def send(request):
    token = request.POST.get('token')

