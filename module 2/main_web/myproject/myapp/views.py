from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import Template, RequestContext
from myproject.myapp.fetch_image.myhttplib import do_fetch_image
from os import getenv
from socket import gethostbyname_ex


def home(request):
    return render(request, 'myapp/home.html', {"message": "CRLF Injection in Request if you can"})


def fetch_image(request):
    if request.method == 'GET' and 'url' in request.GET:
        context = do_fetch_image(request.GET.get('url'),request.GET.get('user_agent'))
        if context == False:
            return redirect("/")
        return render(request, 'myapp/image.html', context)

    template = Template("Invalid request")
    context = RequestContext(request)
    return HttpResponse(template.render(context),status=500,content_type="text/plain")
