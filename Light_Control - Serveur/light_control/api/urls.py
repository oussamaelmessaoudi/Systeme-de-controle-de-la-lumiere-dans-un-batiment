from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'zones', views.ZoneViewSet)
router.register(r'schedules', views.ScheduleViewSet)
router.register(r'permissions', views.PermissionViewSet)
router.register(r'logs', views.ActivityLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]