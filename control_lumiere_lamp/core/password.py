from django.contrib.auth.hashers import make_password
print(make_password('admin123'))  # Pour admin1, admin2
print(make_password('manager123'))  # Pour gestionnaires
print(make_password('resident123'))  # Pour résidents