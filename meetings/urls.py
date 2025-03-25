# meetings/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.meetings_home, name="meetings_home"),
    
    # Widoki kalendarza
    path('calendar/<int:year>/<int:month>/', views.calendar_month_view, name='calendar_month'),
    path('calendar/week/<int:year>/<int:week>/', views.calendar_week_view, name='calendar_week'),
    
    # Zarządzanie spotkaniami
    path('create/', views.meeting_create, name='meeting_create'),
    path('<int:pk>/', views.meeting_detail, name='meeting_detail'),
    path('<int:pk>/edit/', views.meeting_edit, name='meeting_edit'),
    path('<int:pk>/delete/', views.meeting_delete, name='meeting_delete'),
    
    # Zarządzanie uczestnictwem
    path('<int:pk>/response/', views.participant_response, name='participant_response'),
    
    # Zarządzanie przypomnieniami
    path('<int:pk>/reminder/', views.set_reminder, name='set_reminder'),
    path('<int:pk>/reminder/delete/', views.delete_reminder, name='delete_reminder'),
]