from django.urls import path
from . import views  

urlpatterns = [
    # Chemins de base de l'application
    path('', views.dashboard, name='dashboard'),
    path('zone/<int:zone_id>/', views.control_zone, name='control_zone'),
    path('toggle_lamp/<int:lamp_id>/', views.toggle_lamp, name='toggle_lamp'),

    # Chemins de base de l'application
    path('manage-users/', views.manage_users, name='manage_users'),
    path('manage-users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('manage-permissions/', views.manage_permissions, name='manage_permissions'),
    path('manage-permissions/delete/<int:permission_id>/', views.delete_permission, name='delete_permission'),
    path('manage-zones/', views.manage_zones, name='manage_zones'),
    path('manage-zones/delete/<int:zone_id>/', views.delete_zone, name='delete_zone'),
    path('manage-schedules/', views.manage_schedules, name='manage_schedules'),
    path('manage-schedules/delete/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),

    # Statistiques et pistes de données
    path('stats/', views.stats_dashboard, name='stats'),
    path('predictions/<int:zone_id>/', views.predictions_dashboard, name='predictions-dashboard'),
    path('simulation/', views.simulation_view, name='simulation'),

]