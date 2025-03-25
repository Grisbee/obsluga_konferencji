# meetings/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Meeting, MeetingParticipant, Reminder
from django.utils import timezone
import datetime

class DateTimePickerInput(forms.DateTimeInput):
    input_type = 'datetime-local'


class MeetingForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        label="Uczestnicy"
    )
    
    class Meta:
        model = Meeting
        fields = ['title', 'description', 'start_time', 'end_time', 'meeting_link', 'room_code', 'participants']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'start_time': DateTimePickerInput(attrs={'class': 'form-control'}),
            'end_time': DateTimePickerInput(attrs={'class': 'form-control'}),
            'meeting_link': forms.URLInput(attrs={'class': 'form-control'}),
            'room_code': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(MeetingForm, self).__init__(*args, **kwargs)
        
        # Wykluczamy aktualnego użytkownika z listy uczestników
        if self.user:
            self.fields['participants'].queryset = User.objects.exclude(id=self.user.id)
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        # Sprawdzenie czy data rozpoczęcia jest w przyszłości
        if start_time and start_time < timezone.now():
            self.add_error('start_time', 'Data rozpoczęcia musi być w przyszłości')
        
        # Sprawdzenie czy data zakończenia jest późniejsza niż data rozpoczęcia
        if start_time and end_time and end_time <= start_time:
            self.add_error('end_time', 'Czas zakończenia musi być późniejszy niż czas rozpoczęcia')
        
        return cleaned_data
    
    def save(self, commit=True):
        meeting = super().save(commit=False)
        if self.user and not meeting.pk:  # Tylko dla nowego spotkania
            meeting.creator = self.user
        
        if commit:
            meeting.save()
            # Zapisujemy uczestników
            selected_participants = self.cleaned_data.get('participants', [])
            
            # Czyszczenie istniejących powiązań (przy edycji)
            if meeting.pk:
                MeetingParticipant.objects.filter(meeting=meeting).delete()
            
            # Dodawanie uczestników
            for participant in selected_participants:
                MeetingParticipant.objects.create(
                    meeting=meeting,
                    user=participant,
                    status='invited'
                )
            
            self.save_m2m()
        return meeting


class ParticipantResponseForm(forms.ModelForm):
    class Meta:
        model = MeetingParticipant
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'})
        }


class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ['minutes_before']
        widgets = {
            'minutes_before': forms.Select(attrs={'class': 'form-select'})
        }