import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mywebsite.settings')
django.setup()

# Now import the User model
from django.contrib.auth.models import User

# Get the admin user
try:
    admin = User.objects.get(username='admin')
    
    # Set the password
    admin.set_password('admin123')
    
    # Save the user
    admin.save()
    
    print('Password for admin user has been set to "admin123"')
except User.DoesNotExist:
    print('Admin user does not exist')