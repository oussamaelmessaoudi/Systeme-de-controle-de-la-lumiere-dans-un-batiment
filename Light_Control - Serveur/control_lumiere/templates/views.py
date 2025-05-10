from django.shortcuts import render

# Create your views here.
def login_view(request):
    #return HttpResponse('Hello World')
    return render(request, 'login.html')

def dashboard_view(request):
   # return HttpResponse('Bonjour dans Contact')
    return render(request, 'dashboard.html')

def dashboard_admin_view(request):
    return render(request,'dashboard_admin.html')

def gestion_utilisateur_view(request):
    return render(request,'gestion_utilisateur.html')

def gestion_horaire_view(request):
    return render(request,'horaire.html')

def log_view(request):
    return render(request,'log.html')

from django.http import JsonResponse
#from .models import Salle

def toggle_light(request, salle_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        salle = Salle.objects.get(id=salle_id)
        salle.etat = not salle.etat
        salle.dernier_utilisateur = request.user.username
        salle.save()
        
        return JsonResponse({
            'etat': salle.etat,
            'dernier_utilisateur': salle.dernier_utilisateur
        })
    return redirect('dashboard')