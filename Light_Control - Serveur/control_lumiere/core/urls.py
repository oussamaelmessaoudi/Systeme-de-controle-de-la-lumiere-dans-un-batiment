from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("zone/<int:zone_id>/", views.control_zone, name="control_zone"),
]