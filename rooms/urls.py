from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import RoomViewSet

router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')

urlpatterns = [
    path('', include(router.urls)),
] 