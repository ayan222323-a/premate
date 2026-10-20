from django.contrib import admin
from .models import Resume, InterviewSession, InterviewQA

admin.site.register(Resume)
admin.site.register(InterviewSession)
admin.site.register(InterviewQA)