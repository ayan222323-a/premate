from django.urls import path
from . import views

urlpatterns = [
    path('', views.material_list, name='materials'),
    path('note/', views.note_detail, name='note_detail'),
    path('practice/', views.practice_topic, name='practice_topic'),
]