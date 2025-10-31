from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

def home(request):
    return JsonResponse({"message": "Event Management API is running."})

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api/', include('apps.events.urls')),
    path('api/users/', include('apps.users.urls')),

    # ✅ Correct JWT endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
