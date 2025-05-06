from django import forms
from django.contrib.auth.models import User
from .models import Schedule, Zone

class ScheduleForm(forms.ModelForm):
    days_of_week = forms.MultipleChoiceField(
        choices=[
            ('0', 'Lundi'),
            ('1', 'Mardi'),
            ('2', 'Mercredi'),
            ('3', 'Jeudi'),
            ('4', 'Vendredi'),
            ('5', 'Samedi'),
            ('6', 'Dimanche'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    class Meta:
        model = Schedule
        fields = ['zone', 'start_time', 'end_time', 'days_of_week', 'is_active', 'valid_from', 'valid_until']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'valid_from': forms.DateInput(attrs={'type': 'date'}),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Filtrer les zones disponibles selon les permissions
        available_zones = kwargs.pop('available_zones', None)
        
        super().__init__(*args, **kwargs)
        
        if available_zones is not None:
            self.fields['zone'].queryset = available_zones
        
        # Convertir le format de chaîne en liste pour l'affichage du formulaire
        if self.instance.pk and self.instance.days_of_week:
            selected_days = [str(i) for i, day in enumerate(self.instance.days_of_week) if day == '1']
            self.initial['days_of_week'] = selected_days
    
    def clean_days_of_week(self):
        # Convertir la liste de jours sélectionnés en format de chaîne "0010100"
        days = ['0'] * 7
        for day in self.cleaned_data['days_of_week']:
            days[int(day)] = '1'
        return ''.join(days)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email