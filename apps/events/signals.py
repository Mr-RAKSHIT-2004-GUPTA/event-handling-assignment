# apps/events/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RSVP
from .tasks import send_event_update_email

@receiver(post_save, sender=RSVP)
def rsvp_created_handler(sender, instance, created, **kwargs):
    if created:
        # notify organizer (async)
        message = f"{instance.user.username} RSVP'd {instance.status} to {instance.event.title}"
        send_event_update_email.delay(instance.event.id, message)
