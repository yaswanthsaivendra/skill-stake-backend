from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Room, RoomParticipant, RoomStatus
from .serializers import RoomSerializer, RoomParticipantSerializer

class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Room.objects.all()
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_create(self, serializer):
        clerk_user_id = self.request.user.username 
        room = serializer.save(creator=clerk_user_id)
        RoomParticipant.objects.create(
            room=room,
            user=clerk_user_id
        )

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        room = self.get_object()
        
        if not room.is_registration_open:
            return Response(
                {"error": "Registration is closed for this room"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user is already a participant
        if RoomParticipant.objects.filter(room=room, user=request.user.id).exists():
            return Response(
                {"error": "You are already a participant"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create participant and increment counter
        RoomParticipant.objects.create(room=room, user=request.user.id)
        room.current_participants += 1
        room.save()

        return Response(RoomSerializer(room).data)

    @action(detail=True, methods=['post'])
    def start_game(self, request, pk=None):
        room = self.get_object()
        
        # Compare Clerk user IDs
        if room.creator != request.user.username:
            return Response(
                {"error": "Only room creator can start the game"},
                status=status.HTTP_403_FORBIDDEN
            )

        if room.status != RoomStatus.PENDING:
            return Response(
                {"error": "Game has already started or completed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if timezone.now() < room.scheduled_start_time:
            return Response(
                {"error": "Cannot start game before scheduled time"},
                status=status.HTTP_400_BAD_REQUEST
            )

        room.status = RoomStatus.IN_PROGRESS
        room.save()

        return Response(RoomSerializer(room).data)

    @action(detail=True, methods=['post'])
    def submit_score(self, request, pk=None):
        room = self.get_object()
        score = request.data.get('score')

        if room.status != RoomStatus.IN_PROGRESS:
            return Response(
                {"error": "Game is not in progress"},
                status=status.HTTP_400_BAD_REQUEST
            )

        participant = RoomParticipant.objects.filter(
            room=room,
            user=request.user.id
        ).first()

        if not participant:
            return Response(
                {"error": "You are not a participant in this room"},
                status=status.HTTP_400_BAD_REQUEST
            )

        participant.score = score
        participant.completed_at = timezone.now()
        participant.save()

        # Check if all participants have submitted scores
        if not RoomParticipant.objects.filter(
            room=room,
            completed_at__isnull=True
        ).exists():
            room.status = RoomStatus.COMPLETED
            room.save()

        return Response(RoomParticipantSerializer(participant).data)
