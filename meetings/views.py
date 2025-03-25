# meetings/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
import calendar as cal
from .models import Meeting, MeetingParticipant, Reminder
from .forms import MeetingForm, ParticipantResponseForm, ReminderForm

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Pobiera element z słownika za pomocą klucza - przydatne w szablonach."""
    if not dictionary:
        return []
    return dictionary.get(key, [])

def meetings_home(request):
    """Strona główna spotkań - przekierowanie do kalendarza bieżącego miesiąca"""
    now = timezone.now()
    return redirect('calendar_month', year=now.year, month=now.month)

@login_required
def calendar_month_view(request, year=None, month=None):
    """Widok kalendarza miesięcznego"""
    today = timezone.now()
    
    # Jeśli nie podano roku i miesiąca, używamy bieżących wartości
    if year is None:
        year = today.year
    if month is None:
        month = today.month
    
    # Konwersja na liczby całkowite
    year = int(year)
    month = int(month)
    
    # Tworzenie kalendarza dla wybranego miesiąca
    cal_month = cal.monthcalendar(year, month)
    month_name = cal.month_name[month]
    
    # Określanie pierwszego i ostatniego dnia miesiąca
    start_date = datetime(year, month, 1, tzinfo=timezone.get_current_timezone())
    
    # Ustalenie końca miesiąca
    if month == 12:
        end_date = datetime(year + 1, 1, 1, tzinfo=timezone.get_current_timezone())
    else:
        end_date = datetime(year, month + 1, 1, tzinfo=timezone.get_current_timezone())
    
    # Pobieramy spotkania utworzone przez użytkownika oraz te, w których uczestniczy
    meetings = Meeting.objects.filter(
        Q(start_time__gte=start_date, start_time__lt=end_date) &
        (Q(creator=request.user) | Q(participants=request.user))
    ).distinct().order_by('start_time')
    
    # Obliczanie poprzedniego i następnego miesiąca - POPRAWIONA SEKCJA
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
        
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    context = {
        'year': year,
        'month': month,
        'month_name': month_name,
        'calendar': cal_month,
        'meetings': meetings,
        'today': today,
        'prev_month': prev_month,  # Upewnij się, że ta zmienna jest zdefiniowana
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }
    
    return render(request, 'meetings/calendar_month.html', context)

@login_required
def calendar_week_view(request, year=None, week=None):
    """Widok kalendarza tygodniowego"""
    today = timezone.now()
    
    # Jeśli nie podano roku i tygodnia, używamy bieżących wartości
    if year is None:
        year = today.year
    if week is None:
        week = today.isocalendar()[1]  # Numer tygodnia w roku
    
    # Konwersja na liczby całkowite
    year = int(year)
    week = int(week)
    
    # Obliczanie dat początku i końca tygodnia
    first_day_of_year = datetime(year, 1, 1, tzinfo=timezone.get_current_timezone())
    if first_day_of_year.weekday() <= 3:
        # Pierwszy tydzień zawiera pierwszy czwartek roku
        first_week_day = first_day_of_year - timedelta(days=first_day_of_year.weekday())
    else:
        # Pierwszy tydzień zaczyna się od następnego poniedziałku
        first_week_day = first_day_of_year + timedelta(days=(7 - first_day_of_year.weekday()))
    
    start_date = first_week_day + timedelta(weeks=week-1)
    end_date = start_date + timedelta(days=7)
    
    # Pobieramy spotkania utworzone przez użytkownika oraz te, w których uczestniczy
    meetings = Meeting.objects.filter(
        Q(start_time__gte=start_date, start_time__lt=end_date) &
        (Q(creator=request.user) | Q(participants=request.user))
    ).distinct().order_by('start_time')
    
    # Tworzymy listę dni
    days = []
    for i in range(7):
        days.append(start_date + timedelta(days=i))
    
    # Obliczanie poprzedniego i następnego tygodnia - POPRAWIONA SEKCJA
    if week == 1:
        prev_week = 52  # Zakładamy, że poprzedni rok ma 52 tygodnie
        prev_year = year - 1
    else:
        prev_week = week - 1
        prev_year = year
        
    if week == 52:  # Zakładamy, że większość lat ma 52 tygodnie
        next_week = 1
        next_year = year + 1
    else:
        next_week = week + 1
        next_year = year
    
    # Dodajmy godziny jako pełne obiekty, nie tylko stringi
    hours = []
    for h in range(7, 23):  # Od 7:00 do 22:00
        hours.append(h)
    
    context = {
        'year': year,
        'week': week,
        'days': days,
        'hours': hours,
        'meetings': meetings,
        'today': today,
        'prev_week': prev_week,  # Upewnij się, że ta zmienna jest zdefiniowana
        'prev_year': prev_year,
        'next_week': next_week,
        'next_year': next_year,
    }
    
    return render(request, 'meetings/calendar_week.html', context)

@login_required
def meeting_create(request):
    """Tworzenie nowego spotkania"""
    if request.method == 'POST':
        form = MeetingForm(request.POST, user=request.user)
        if form.is_valid():
            meeting = form.save()
            messages.success(request, 'Spotkanie zostało utworzone pomyślnie.')
            return redirect('meeting_detail', pk=meeting.pk)
    else:
        # Domyślnie proponujemy spotkanie rozpoczynające się za godzinę i trwające 1h
        initial_start = timezone.now() + timedelta(hours=1)
        initial_start = initial_start.replace(minute=0, second=0, microsecond=0)  # Zaokrąglamy do pełnej godziny
        initial_end = initial_start + timedelta(hours=1)
        
        form = MeetingForm(user=request.user, initial={
            'start_time': initial_start,
            'end_time': initial_end,
        })
    
    return render(request, 'meetings/meeting_form.html', {
        'form': form,
        'is_new': True
    })

@login_required
def meeting_edit(request, pk):
    """Edycja istniejącego spotkania"""
    meeting = get_object_or_404(Meeting, pk=pk)
    
    # Sprawdzamy czy użytkownik jest twórcą spotkania
    if meeting.creator != request.user:
        messages.error(request, 'Nie masz uprawnień do edycji tego spotkania.')
        return redirect('meeting_detail', pk=meeting.pk)
    
    if request.method == 'POST':
        form = MeetingForm(request.POST, instance=meeting, user=request.user)
        if form.is_valid():
            meeting = form.save()
            messages.success(request, 'Spotkanie zostało zaktualizowane.')
            return redirect('meeting_detail', pk=meeting.pk)
    else:
        # Pobieramy aktualnych uczestników
        initial_participants = meeting.participants.exclude(id=request.user.id)
        form = MeetingForm(instance=meeting, user=request.user, initial={
            'participants': initial_participants
        })
    
    return render(request, 'meetings/meeting_form.html', {
        'form': form,
        'meeting': meeting,
        'is_new': False
    })

@login_required
def meeting_detail(request, pk):
    """Szczegóły spotkania"""
    meeting = get_object_or_404(Meeting, pk=pk)
    
    # Sprawdzamy czy użytkownik ma dostęp do tego spotkania
    if meeting.creator != request.user and not meeting.participants.filter(id=request.user.id).exists():
        messages.error(request, 'Nie masz dostępu do tego spotkania.')
        return redirect('meetings_home')
    
    # Inicjalizacja zmiennej participant przed użyciem
    participant = None
    participant_status = None
    
    # Jeśli użytkownik jest uczestnikiem, pobieramy jego status
    if request.user != meeting.creator:
        participant = MeetingParticipant.objects.filter(meeting=meeting, user=request.user).first()
        if participant:
            participant_status = participant.status
    
    # Pobieramy przypomnienie użytkownika dla tego spotkania (jeśli istnieje)
    reminder = Reminder.objects.filter(meeting=meeting, user=request.user).first()
    
    context = {
        'meeting': meeting,
        'is_creator': meeting.creator == request.user,
        'participant_status': participant_status,
        'reminder': reminder,
        'participant_form': ParticipantResponseForm(instance=participant) if participant else None,
        'reminder_form': ReminderForm(instance=reminder) if reminder else ReminderForm(),
    }
    
    return render(request, 'meetings/meeting_detail.html', context)

@login_required
def meeting_delete(request, pk):
    """Usuwanie spotkania"""
    meeting = get_object_or_404(Meeting, pk=pk)
    
    # Sprawdzamy czy użytkownik jest twórcą spotkania
    if meeting.creator != request.user:
        messages.error(request, 'Nie masz uprawnień do usunięcia tego spotkania.')
        return redirect('meeting_detail', pk=meeting.pk)
    
    if request.method == 'POST':
        meeting.delete()
        messages.success(request, 'Spotkanie zostało usunięte.')
        return redirect('meetings_home')
    
    return render(request, 'meetings/meeting_confirm_delete.html', {'meeting': meeting})

@login_required
def participant_response(request, pk):
    """Odpowiedź uczestnika na zaproszenie"""
    meeting = get_object_or_404(Meeting, pk=pk)
    participant = get_object_or_404(MeetingParticipant, meeting=meeting, user=request.user)
    
    if request.method == 'POST':
        form = ParticipantResponseForm(request.POST, instance=participant)
        if form.is_valid():
            participant = form.save(commit=False)
            participant.response_at = timezone.now()
            participant.save()
            messages.success(request, 'Twoja odpowiedź została zapisana.')
    
    return redirect('meeting_detail', pk=meeting.pk)

@login_required
def set_reminder(request, pk):
    """Ustawienie przypomnienia dla spotkania"""
    meeting = get_object_or_404(Meeting, pk=pk)
    
    # Sprawdzamy czy użytkownik ma dostęp do tego spotkania
    if meeting.creator != request.user and not meeting.participants.filter(id=request.user.id).exists():
        messages.error(request, 'Nie masz dostępu do tego spotkania.')
        return redirect('meetings_home')
    
    if request.method == 'POST':
        # Sprawdzamy czy istnieje już przypomnienie
        reminder, created = Reminder.objects.get_or_create(
            meeting=meeting,
            user=request.user,
            defaults={'minutes_before': 15}
        )
        
        form = ReminderForm(request.POST, instance=reminder)
        if form.is_valid():
            form.save()
            messages.success(request, 'Przypomnienie zostało ustawione.')
    
    return redirect('meeting_detail', pk=meeting.pk)

@login_required
def delete_reminder(request, pk):
    """Usunięcie przypomnienia"""
    meeting = get_object_or_404(Meeting, pk=pk)
    reminder = get_object_or_404(Reminder, meeting=meeting, user=request.user)
    
    if request.method == 'POST':
        reminder.delete()
        messages.success(request, 'Przypomnienie zostało usunięte.')
    
    return redirect('meeting_detail', pk=meeting.pk)

@login_required
def toggle_meeting_active(request, pk):
    """Aktywacja/deaktywacja spotkania przez właściciela"""
    meeting = get_object_or_404(Meeting, pk=pk)
    
    # Tylko właściciel może aktywować/deaktywować spotkanie
    if meeting.creator != request.user:
        messages.error(request, 'Tylko organizator spotkania może je aktywować lub deaktywować.')
        return redirect('meeting_detail', pk=meeting.pk)
    
    # Zmień stan aktywności
    meeting.is_active = not meeting.is_active
    meeting.save()
    
    if meeting.is_active:
        messages.success(request, 'Spotkanie zostało aktywowane. Uczestnicy mogą teraz dołączyć.')
    else:
        messages.success(request, 'Spotkanie zostało dezaktywowane.')
    
    return redirect('meeting_detail', pk=meeting.pk)