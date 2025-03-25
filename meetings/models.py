# meetings/models.py
from django.db import models
from django.contrib.auth.models import User

class Meeting(models.Model):
    title = models.CharField(max_length=200, verbose_name="Tytuł")
    description = models.TextField(blank=True, null=True, verbose_name="Opis")
    start_time = models.DateTimeField(verbose_name="Czas rozpoczęcia")
    end_time = models.DateTimeField(verbose_name="Czas zakończenia")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data aktualizacji")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_meetings", verbose_name="Organizator")
    participants = models.ManyToManyField(User, through='MeetingParticipant', related_name="meetings", verbose_name="Uczestnicy")
    meeting_link = models.URLField(blank=True, null=True, verbose_name="Link do spotkania")
    room_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="Kod pokoju")
    is_active = models.BooleanField(default=False, verbose_name="Aktywne")
    
    class Meta:
        ordering = ['start_time']
        verbose_name = "Spotkanie"
        verbose_name_plural = "Spotkania"
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('meeting_detail', args=[str(self.id)])
    
    @property
    def duration_minutes(self):
        """Zwraca czas trwania spotkania w minutach"""
        delta = self.end_time - self.start_time
        return delta.total_seconds() // 60


class MeetingParticipant(models.Model):
    STATUS_CHOICES = (
        ('invited', 'Zaproszony'),
        ('accepted', 'Zaakceptował'),
        ('declined', 'Odrzucił'),
        ('tentative', 'Niepewny'),
    )
    
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="meeting_participants")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meeting_invitations")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='invited', verbose_name="Status")
    invited_at = models.DateTimeField(auto_now_add=True, verbose_name="Data zaproszenia")
    response_at = models.DateTimeField(blank=True, null=True, verbose_name="Data odpowiedzi")
    
    class Meta:
        unique_together = ('meeting', 'user')
        verbose_name = "Uczestnik spotkania"
        verbose_name_plural = "Uczestnicy spotkania"
    
    def __str__(self):
        return f"{self.user.username} - {self.meeting.title}"


class Reminder(models.Model):
    REMINDER_CHOICES = (
        (5, '5 minut'),
        (10, '10 minut'),
        (15, '15 minut'),
        (30, '30 minut'),
        (60, '1 godzina'),
        (120, '2 godziny'),
        (1440, '1 dzień'),
    )
    
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="reminders")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meeting_reminders")
    minutes_before = models.IntegerField(choices=REMINDER_CHOICES, default=15, verbose_name="Czas przypomnienia")
    sent = models.BooleanField(default=False, verbose_name="Wysłano")
    
    class Meta:
        unique_together = ('meeting', 'user', 'minutes_before')
        verbose_name = "Przypomnienie"
        verbose_name_plural = "Przypomnienia"
    
    def __str__(self):
        return f"Przypomnienie: {self.meeting.title} dla {self.user.username}, {self.minutes_before} min przed"