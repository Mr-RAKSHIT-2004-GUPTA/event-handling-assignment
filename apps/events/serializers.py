from rest_framework import serializers
from .models import Event, RSVP, Review
from django.contrib.auth.models import User
from .models import Invitation

class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.ReadOnlyField(source='organizer.username')

    class Meta:
        model = Event
        fields = '__all__'


class RSVPSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = RSVP
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Review
        fields = '__all__'


class InvitationSerializer(serializers.ModelSerializer):
    invitee_username = serializers.ReadOnlyField(source='invitee.username')
    invited_by_username = serializers.ReadOnlyField(source='invited_by.username')

    class Meta:
        model = Invitation
        fields = ['id', 'event', 'invitee', 'invitee_username', 'invited_by', 'invited_by_username', 'accepted', 'created_at', 'expires_at']
        read_only_fields = ['invited_by', 'created_at', 'invitee_username', 'invited_by_username']
