from django.urls import path
from . import views

urlpatterns = [
    path('', views.exam_select, name='exam_select'),
    path('take/<int:attempt_id>/', views.take_test, name='take_test'),
    path('result/<int:attempt_id>/', views.test_result, name='test_result'),
]