# meetings/admin.py
from django.contrib import admin
from .models import Meeting, MeetingParticipant, Reminder

class MeetingParticipantInline(admin.TabularInline):
    model = MeetingParticipant
    extra = 1

class ReminderInline(admin.TabularInline):
    model = Reminder
    extra = 1

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'creator', 'created_at')
    list_filter = ('start_time', 'creator')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_time'
    inlines = [MeetingParticipantInline, ReminderInline]

@admin.register(MeetingParticipant)
class MeetingParticipantAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'user', 'status', 'invited_at', 'response_at')
    list_filter = ('status', 'invited_at')
    search_fields = ('meeting__title', 'user__username')

@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'user', 'minutes_before', 'sent')
    list_filter = ('minutes_before', 'sent')
    search_fields = ('meeting__title', 'user__username')