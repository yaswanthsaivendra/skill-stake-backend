from rest_framework import serializers
from .models import Room, RoomParticipant

class RoomParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomParticipant
        fields = ['id', 'user', 'score', 'completed_at']
        read_only_fields = ['completed_at']

class RoomSerializer(serializers.ModelSerializer):
    creator = serializers.CharField(read_only=True)
    participants = RoomParticipantSerializer(many=True, read_only=True)
    prize_distribution = serializers.SerializerMethodField()
    is_registration_open = serializers.BooleanField(read_only=True)

    class Meta:
        model = Room
        fields = [
            'id', 'title', 'description', 'creator', 'current_participants',
            'entry_fee', 'difficulty_level', 'scheduled_start_time',
            'registration_deadline', 'is_active', 'status', 'duration_minutes',
            'started_at', 'participants', 'prize_distribution', 'is_registration_open'
        ]
        read_only_fields = ['current_participants', 'started_at', 'status', 'creator']

    def get_prize_distribution(self, obj):
        return obj.get_prize_distribution()