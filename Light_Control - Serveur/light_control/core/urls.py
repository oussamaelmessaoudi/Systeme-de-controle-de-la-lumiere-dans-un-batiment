from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('zones/', views.zone_list, name='zone_list'),
    path('zones/<int:pk>/', views.zone_detail, name='zone_detail'),
    path('schedules/', views.schedule_list, name='schedule_list'),
    path('schedules/create/', views.schedule_create, name='schedule_create'),
    path('schedules/<int:pk>/edit/', views.schedule_edit, name='schedule_edit'),
    path('schedules/<int:pk>/delete/', views.schedule_delete, name='schedule_delete'),
    path('logs/', views.activity_log, name='activity_log'),
    path('profile/', views.user_profile, name='user_profile'),
]