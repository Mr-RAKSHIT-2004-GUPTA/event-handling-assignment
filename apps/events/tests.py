# apps/events/tests.py
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Event, Invitation, RSVP, Review
from django.utils import timezone
from datetime import timedelta

def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

class EventFlowTests(APITestCase):

    def setUp(self):
        # users
        self.organizer = User.objects.create_user(username='org', password='pass', email='org@example.com')
        self.alice = User.objects.create_user(username='alice', password='pass', email='alice@example.com')
        self.bob = User.objects.create_user(username='bob', password='pass', email='bob@example.com')

        # public event
        self.public_event = Event.objects.create(
            title='Public Event',
            description='Open to all',
            organizer=self.organizer,
            location='HQ',
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=2),
            is_public=True
        )

        # private event
        self.private_event = Event.objects.create(
            title='Private Event',
            description='Invite only',
            organizer=self.organizer,
            location='Secret',
            start_time=timezone.now() + timedelta(days=2),
            end_time=timezone.now() + timedelta(days=2, hours=2),
            is_public=False
        )

    def test_public_event_visible_to_anonymous(self):
        url = reverse('event-list')  # router name
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        titles = [e['title'] for e in resp.json()['results']]
        self.assertIn('Public Event', titles)
        self.assertNotIn('Private Event', titles)

    def test_private_event_visible_to_invited_user(self):
        # invite alice
        Invitation.objects.create(event=self.private_event, invitee=self.alice, invited_by=self.organizer)
        token = get_token_for_user(self.alice)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        resp = self.client.get(reverse('event-list'))
        self.assertEqual(resp.status_code, 200)
        titles = [e['title'] for e in resp.json()['results']]
        self.assertIn('Private Event', titles)

    def test_organizer_can_invite(self):
        token = get_token_for_user(self.organizer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = reverse('event-invite', kwargs={'pk': self.private_event.id})
        resp = self.client.post(url, {'invitee': self.bob.id})
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Invitation.objects.filter(event=self.private_event, invitee=self.bob).exists())

    def test_rsvp_create_and_update_by_owner(self):
        token = get_token_for_user(self.alice)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = reverse('event-rsvp', kwargs={'event_id': self.public_event.id})
        resp = self.client.post(url, {'status': 'Going'})
        self.assertEqual(resp.status_code, 201)
        rsvp = RSVP.objects.get(event=self.public_event, user=self.alice)
        # organizer updates rsvp status of alice
        token_org = get_token_for_user(self.organizer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_org}')
        url_update = reverse('event-rsvp-update', kwargs={'event_id': self.public_event.id, 'user_id': self.alice.id})
        resp2 = self.client.patch(url_update, {'status': 'Maybe'}, format='json')
        self.assertEqual(resp2.status_code, 200)
        rsvp.refresh_from_db()
        self.assertEqual(rsvp.status, 'Maybe')

    def test_add_review(self):
        token = get_token_for_user(self.alice)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = reverse('event-reviews', kwargs={'event_id': self.public_event.id})
        resp = self.client.post(url, {'rating': 4, 'comment': 'Nice event'})
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Review.objects.filter(event=self.public_event, user=self.alice).exists())
