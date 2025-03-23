from django.shortcuts import render

def meetings_home(request):
    return render(request, 'base.html')