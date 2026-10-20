from django.contrib import admin
from .models import TestAttempt, AttemptQuestion

admin.site.register(TestAttempt)
admin.site.register(AttemptQuestion)