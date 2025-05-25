# meetings/zoom_api.py
import requests
from django.conf import settings
import base64

def get_zoom_access_token():
    url = 'https://zoom.us/oauth/token'
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(
            f"{settings.ZOOM_CLIENT_ID}:{settings.ZOOM_CLIENT_SECRET}".encode()
        ).decode(),
    }
    params = {
        'grant_type': 'account_credentials',
        'account_id': settings.ZOOM_ACCOUNT_ID,
    }
    response = requests.post(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()['access_token']

def create_zoom_meeting(topic, start_time, duration_minutes):
    token = get_zoom_access_token()
    url = f'{settings.ZOOM_API_BASE_URL}users/me/meetings'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    payload = {
        'topic': topic,
        'type': 2,  # zaplanowane spotkanie
        'start_time': start_time.isoformat(),
        'duration': duration_minutes,
        'timezone': 'UTC',
        'settings': {
            'join_before_host': True,
            'approval_type': 0,
            'meeting_authentication': False,
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
