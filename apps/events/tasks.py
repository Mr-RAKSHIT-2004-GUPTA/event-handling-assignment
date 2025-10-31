# apps/events/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from .models import Invitation, RSVP, Event
from django.conf import settings

@shared_task
def send_invite_email(invitation_id):
    try:
        invitation = Invitation.objects.select_related('event','invitee','invited_by').get(id=invitation_id)
    except Invitation.DoesNotExist:
        return False

    subject = f"You've been invited to {invitation.event.title}"
    body = f"Hi {invitation.invitee.username},\n\n" \
           f"You have been invited by {invitation.invited_by.username} to the event '{invitation.event.title}'.\n" \
           f"Event starts at: {invitation.event.start_time}\n\n" \
           "Visit the app to RSVP.\n\nThanks."
    recipient = [invitation.invitee.email] if invitation.invitee.email else []

    if not recipient:
        return False

    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipient, fail_silently=True)
    return True

@shared_task
def send_event_update_email(event_id, message):
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return False

    # notify all RSVPed users
    recipients = list(event.rsvps.select_related('user').values_list('user__email', flat=True))
    recipients = [r for r in recipients if r]
    if not recipients:
        return False

    send_mail(f"Update: {event.title}", message, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=True)
    return True
