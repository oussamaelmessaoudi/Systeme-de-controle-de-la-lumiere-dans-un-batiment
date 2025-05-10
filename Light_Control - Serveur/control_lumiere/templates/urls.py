"""light_control URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from batiment import views
from django.contrib.auth.views import LoginView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.login_view),
    path('dashboard/',views.dashboard_view),
    path('toggle/<int:salle_id>/', views.toggle_light, name='toggle_light'),
    #path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('dashboard_admin/',views.dashboard_admin_view),
    path('gestion_utilisateur/',views.gestion_utilisateur_view),
    path('horaire/',views.gestion_horaire_view),
    path('log/',views.log_view),
]


