from django.db import models
from django.contrib.auth.models import User


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(upload_to='resumes/')
    extracted_text = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"


class InterviewSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interviews')
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    job_role = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    overall_score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.job_role}"


class InterviewQA(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='qas')
    question = models.TextField()
    answer = models.TextField(blank=True)
    feedback = models.TextField(blank=True)
    score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.question[:50]