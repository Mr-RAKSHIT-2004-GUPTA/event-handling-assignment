# apps/events/views.py
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import models
from .models import Event, RSVP, Review, Invitation
from .serializers import EventSerializer, RSVPSerializer, ReviewSerializer, InvitationSerializer
from .permissions import IsOrganizerOrReadOnly, CanAccessEvent
from rest_framework.permissions import IsAuthenticated

class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOrganizerOrReadOnly]
    filterset_fields = ['location', 'organizer']
    search_fields = ['title', 'description']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            # anonymous users only see public events
            return Event.objects.filter(is_public=True)
        # authenticated: public events OR events where user is organizer OR invited
        invited_event_ids = Invitation.objects.filter(invitee=user).values_list('event_id', flat=True)
        return Event.objects.filter(
            models.Q(is_public=True) |
            models.Q(organizer=user) |
            models.Q(id__in=invited_event_ids)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    def get_permissions(self):
        if self.action in ['retrieve', 'list']:
            return [permissions.AllowAny()]  # visibility enforced via get_queryset
        return super().get_permissions()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def invite(self, request, pk=None):
        """
        POST /events/{id}/invite/
        body: { "invitee": <user_id>, "expires_at": "<ISO datetime (optional)>" }
        Only organizer can invite.
        """
        event = self.get_object()
        if event.organizer != request.user:
            return Response({"detail": "Only organizer can invite."}, status=status.HTTP_403_FORBIDDEN)

        invitee_id = request.data.get('invitee')
        if not invitee_id:
            return Response({"detail": "invitee (user id) is required."}, status=status.HTTP_400_BAD_REQUEST)

        invitee = get_object_or_404(User, id=invitee_id)
        expires_at = request.data.get('expires_at', None)
        invitation, created = Invitation.objects.get_or_create(
            event=event, invitee=invitee,
            defaults={'invited_by': request.user, 'expires_at': expires_at}
        )
        if not created:
            return Response({"detail": "User already invited."}, status=status.HTTP_400_BAD_REQUEST)

        # Optionally fire Celery task to email invite
        try:
            from .tasks import send_invite_email
            send_invite_email.delay(invitation.id)
        except Exception:
            pass

        serializer = InvitationSerializer(invitation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RSVPCreateView(generics.CreateAPIView):
    serializer_class = RSVPSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        event_id = self.kwargs['event_id']
        event = get_object_or_404(Event, id=event_id)
        serializer.save(user=self.request.user, event=event)


class RSVPUpdateView(generics.UpdateAPIView):
    """
    PATCH /events/{event_id}/rsvp/{user_id}/
    Only the RSVP owner or event organizer can change status.
    """
    serializer_class = RSVPSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'rsvp_pk'  # not used directly; we'll fetch object manually

    def get_object(self):
        event_id = self.kwargs['event_id']
        user_id = self.kwargs['user_id']
        return get_object_or_404(RSVP, event_id=event_id, user_id=user_id)

    def patch(self, request, *args, **kwargs):
        rsvp = self.get_object()
        # allow only rsvp owner or event organizer
        if not (request.user == rsvp.user or request.user == rsvp.event.organizer):
            return Response({"detail": "Not permitted."}, status=status.HTTP_403_FORBIDDEN)
        return self.partial_update(request, *args, **kwargs)


class ReviewView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(event_id=self.kwargs['event_id'])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, event_id=self.kwargs['event_id'])
