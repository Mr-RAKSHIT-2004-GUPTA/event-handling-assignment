# apps/events/permissions.py
from rest_framework import permissions

class IsOrganizerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # SAFE methods are allowed for view-level but we'll enforce private event visibility elsewhere
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.organizer == request.user

class CanAccessEvent(permissions.BasePermission):
    """
    Allows access to an Event if:
    - event.is_public is True OR
    - request.user is organizer OR
    - request.user has an active Invitation for this event
    """
    def has_object_permission(self, request, view, obj):
        # obj is Event instance
        if obj.is_public:
            return True
        if request.user and request.user.is_authenticated:
            if obj.organizer == request.user:
                return True
            # check invitations
            return obj.invitations.filter(invitee=request.user).exists()
        return False
