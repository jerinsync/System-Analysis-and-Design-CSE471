from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from .models import Client

@receiver(user_signed_up)
def create_client_for_new_user(request, user, **kwargs):
    # Ensure that all relevant data is populated before creating the Client
    if not Client.objects.filter(user=user).exists():
        # Create the Client instance only if the user data is fully populated
        Client.objects.create(
            user=user,
            client_usrname=user.username,
            email=user.email,
            # Optional: Include first_name and last_name if needed
            first_name=user.first_name,
            last_name=user.last_name
            
        )
