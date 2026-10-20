from datetime import timedelta
from django.utils import timezone


def calculate_streak(dates):
    """dates: set of date objects jis din user ne kuch kiya."""
    if not dates:
        return 0
    today = timezone.localdate()
    day = today if today in dates else today - timedelta(days=1)
    streak = 0
    while day in dates:
        streak += 1
        day -= timedelta(days=1)
    return streak