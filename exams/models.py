from django.db import models
from django.contrib.auth.models import User


class TestAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts')
    subject = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=20)
    total = models.PositiveIntegerField(default=0)
    score = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.subject} ({self.score}/{self.total})"


class AttemptQuestion(models.Model):
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    options = models.JSONField()
    correct_index = models.PositiveSmallIntegerField()
    explanation = models.TextField(blank=True)
    subtopic = models.CharField(max_length=100, blank=True)
    selected_index = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return self.text[:50]