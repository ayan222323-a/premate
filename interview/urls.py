from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_resume, name='upload_resume'),
    path('room/<int:session_id>/', views.interview_room, name='interview_room'),
    path('session/<int:session_id>/', views.session_detail, name='session_detail'),
]