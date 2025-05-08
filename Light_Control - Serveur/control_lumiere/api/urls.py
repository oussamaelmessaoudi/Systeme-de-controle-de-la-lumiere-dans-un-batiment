from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"zones", views.ZoneViewSet)
router.register(r"schedules", views.ScheduleViewSet)
router.register(r"permissions", views.PermissionViewSet)
router.register(r"activity-logs", views.ActivityLogViewSet)

urlpatterns = [
    path("", include(router.urls)),
]