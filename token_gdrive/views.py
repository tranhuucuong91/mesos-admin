from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import subprocess
from django.views.decorators.csrf import csrf_exempt
from token_gdrive.models import *
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied

# Create your views here.
@login_required
def index(request):
    return render(request, 'token_gdrive/index.html')

@login_required
def add_token(request):
    if request.method == 'GET':
        token = request.GET.get('token', None)
        process = subprocess.Popen(['python2', "{}/gdrive.py".format(settings.DIR_GDRIVE_AUTH), token], cwd=settings.DIR_GDRIVE_AUTH, stdout=subprocess.PIPE)
        out, err = process.communicate()
        credential = Credentials()
        credential.credential = out.decode().split("\n")[1]
        credential.gmail = request.GET.get('gmail', None)
        credential.save()
        return HttpResponse(out.decode().split("\n")[1])
    else:
        return HttpResponse("no sp")

@login_required
def list_token(request):
    credentials = Credentials.objects.all()
    data = {"credentials": credentials}
    return render(request, 'token_gdrive/list_token.html', data)

@csrf_exempt
@login_required
@permission_required('token_gdrive.delete_credential', raise_exception=True)
def credential_action(request):
    try:
        if request.method == 'POST':
            action = request.POST.get('action', None)
            if action == 'delete':
                id = request.POST.get('id')
                credential = Credentials.objects.get(pk=id)
                credential.delete()
            elif action == 'start':
                pass

            result = '{"status":"success", "msg": "%(action)s success"}'%{"action":action}
    except Exception as e:
        result = '{"status":"error", "msg": "%(action)s fail: %(error)s" }'%{"action":action, "error": str(e).replace("\n", " ").replace('"', '\\"')}
    return HttpResponse(result)
