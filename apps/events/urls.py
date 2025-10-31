# apps/events/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, RSVPCreateView, RSVPUpdateView, ReviewView

# Register standard CRUD endpoints for Events
router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    # CRUD routes for Event (list, create, retrieve, update, delete)
    path('', include(router.urls)),

    # Custom endpoints for RSVP and Reviews
    path('events/<int:event_id>/rsvp/', RSVPCreateView.as_view(), name='event-rsvp'),
    path('events/<int:event_id>/rsvp/<int:user_id>/', RSVPUpdateView.as_view(), name='event-rsvp-update'),
    path('events/<int:event_id>/reviews/', ReviewView.as_view(), name='event-reviews'),
]
