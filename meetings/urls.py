# meetings/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.meetings_home, name="base"),
]