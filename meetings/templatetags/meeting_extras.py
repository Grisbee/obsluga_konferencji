# meetings/templatetags/meeting_extras.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Pobiera element z słownika za pomocą klucza - przydatne w szablonach."""
    if not dictionary:
        return []
    return dictionary.get(key, [])