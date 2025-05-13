from django.contrib import admin
from django.urls import path, include
from django.urls import path, include
from core.views import UsageFrequencyView, EnergyConsumptionView, stats_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', include('core.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/stats/usage-frequency/', UsageFrequencyView.as_view(), name='usage-frequency'),
    path('api/stats/energy-consumption/', EnergyConsumptionView.as_view(), name='energy-consumption'),
    path('stats/', stats_dashboard, name='stats'),
    path('', include('core.urls')),
]