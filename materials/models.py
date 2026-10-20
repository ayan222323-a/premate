from django.db import models
from django.contrib.auth.models import User


class StudyNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_notes')
    topic = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'topic')

    def __str__(self):
        return f"{self.user.username} - {self.topic}"