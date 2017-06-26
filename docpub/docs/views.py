from django.shortcuts import render
from django.template.context import RequestContext


def index(request):
   context = {'user': request.user}
   return render(request, 'index.html', context)


# from django.shortcuts import render
# from django.http import HttpResponse


# def index(request):
#     return HttpResponse("Hello, world. You're at the polls index.")

