# core/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from core.models import ActivityLog, Analytics
from sklearn.ensemble import RandomForestClassifier
import pandas as pd


@shared_task
def compute_analytics():
    # Période des dernières 24h
    start_time = timezone.now() - timedelta(days=1)
    logs = ActivityLog.objects.filter(
        timestamp__gte=start_time,
        action__in=['turn_on', 'turn_off']
    ).values('zone_id', 'action', 'timestamp')
    
    # Calculer la fréquence d'utilisation (nombre d'actions 'turn_on')
    for zone_id in set(log['zone_id'] for log in logs):
        zone_logs = [log for log in logs if log['zone_id'] == zone_id]
        turn_on_count = sum(1 for log in zone_logs if log['action'] == 'turn_on')
        
        # Estimer la consommation (durée d'allumage en heures)
        duration_hours = 0
        last_turn_on = None
        for log in sorted(zone_logs, key=lambda x: x['timestamp']):
            if log['action'] == 'turn_on':
                last_turn_on = log['timestamp']
            elif log['action'] == 'turn_off' and last_turn_on:
                duration_hours += (log['timestamp'] - last_turn_on).total_seconds() / 3600
                last_turn_on = None
        
        # Supposons 100W par heure pour la consommation (exemple)
        energy_consumption = duration_hours * 100  # Wh
        
        # Enregistrer dans core_analytics
        Analytics.objects.create(
            zone_id=zone_id,
            metric_type='usage_frequency',
            metric_value=turn_on_count
        )
        Analytics.objects.create(
            zone_id=zone_id,
            metric_type='energy_consumption',
            metric_value=energy_consumption
        )

@shared_task
def train_prediction_model():
    # Collecter les logs des 30 derniers jours
    start_time = timezone.now() - timedelta(days=30)
    logs = ActivityLog.objects.filter(
        timestamp__gte=start_time,
        action__in=['turn_on', 'turn_off']
    ).values('zone_id', 'timestamp', 'action')
    
    # Préparer les données
    df = pd.DataFrame(logs)
    if df.empty:
        return  # Pas assez de données
    
    df['hour'] = df['timestamp'].dt.hour
    df['day'] = df['timestamp'].dt.dayofweek
    X = df[['hour', 'day']]
    y = df['action'].apply(lambda x: 1 if x == 'turn_on' else 0)
    
    # Entraîner le modèle
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Sauvegarder le modèle (simplifié, dans un fichier)
    import joblib
    joblib.dump(model, 'rf_model.pkl')

@shared_task
def predict_usage_patterns():
    import joblib
    model = joblib.load('rf_model.pkl')
    
    # Prédire pour les 24 prochaines heures
    for zone_id in ActivityLog.objects.values('zone_id').distinct():
        zone_id = zone_id['zone_id']
        for hour in range(24):
            pred = model.predict([[hour, timezone.now().weekday()]])[0]
            if pred > 0.5:  # Seuil pour allumer
                Schedule.objects.update_or_create(
                    zone_id=zone_id,
                    start_time=f'{hour:02d}:00',
                    defaults={
                        'end_time': f'{(hour+1)%24:02d}:00',
                        'action': 'turn_on',
                        'days': 'Mon,Tue,Wed,Thu,Fri,Sat,Sun',
                        'is_active': True,
                        'valid_from': timezone.now().date(),
                        'valid_until': None
                    }
                )