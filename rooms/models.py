from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from core.models import BaseModel
from django.core.exceptions import ValidationError

class DifficultyLevel(models.TextChoices):
    EASY = 'EASY', 'Easy'
    MEDIUM = 'MEDIUM', 'Medium'
    HARD = 'HARD', 'Hard'
    VERY_HARD = 'VERY_HARD', 'Very Hard'

class RoomStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'  # Room created but not started
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'  # Game is ongoing
    COMPLETED = 'COMPLETED', 'Completed'  # Game has ended

class Room(BaseModel):
    MAX_PARTICIPANTS = 15
    MIN_ENTRY_FEE = 100  # Minimum entry fee in rupees
    PLATFORM_FEE_PERCENTAGE = 30  # 30% platform fee
    MIN_PARTICIPANTS = 2  # Add this constant

    # Prize distribution rules based on participant count
    PRIZE_DISTRIBUTION = {
        # participants: [(position, percentage), ...]
        5: [(1, 100)],  # 1-5 players: winner takes all
        10: [(1, 70), (2, 30)],  # 6-10 players: first gets 70%, second gets 30%
        15: [(1, 50), (2, 30), (3, 20)]  # 11-15 players: first 50%, second 30%, third 20%
    }

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    creator = models.CharField(max_length=255)  # Clerk user ID
    current_participants = models.PositiveIntegerField(default=1)  # Starts at 1 because creator joins automatically
    entry_fee = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_ENTRY_FEE)],
        help_text=f"Minimum entry fee is ₹{MIN_ENTRY_FEE}"
    )
    difficulty_level = models.CharField(
        max_length=10,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.MEDIUM
    )
    scheduled_start_time = models.DateTimeField()
    registration_deadline = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20,
        choices=RoomStatus.choices,
        default=RoomStatus.PENDING
    )
    duration_minutes = models.PositiveIntegerField(
        default=30,
        help_text="Duration of the game in minutes"
    )
    started_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-scheduled_start_time']

    def clean(self):
        if self.registration_deadline >= self.scheduled_start_time:
            raise ValidationError('Registration deadline must be before start time')
        
        if self.entry_fee < self.MIN_ENTRY_FEE:
            raise ValidationError(f'Entry fee must be at least ₹{self.MIN_ENTRY_FEE}')

    def save(self, *args, **kwargs):
        # Set started_at when status changes to IN_PROGRESS
        if self.status == RoomStatus.IN_PROGRESS and not self.started_at:
            self.started_at = timezone.now()
        self.clean()
        super().save(*args, **kwargs)

    def close_room(self):
        """Close the room and mark it as inactive"""
        self.is_active = False
        self.status = RoomStatus.COMPLETED  # or create a new status like CANCELLED
        self.save()

    @property
    def is_registration_open(self):
        """Check if registration is still open"""
        return (
            self.is_active and 
            self.status == RoomStatus.PENDING and
            timezone.now() < self.registration_deadline and
            self.current_participants < self.MAX_PARTICIPANTS
        )

    @property
    def has_minimum_participants(self):
        """Check if room has minimum required participants"""
        return self.current_participants >= self.MIN_PARTICIPANTS

    def get_prize_distribution(self):
        """
        Returns the prize distribution based on current participant count
        """
        total_pool = self.current_participants * self.entry_fee
        platform_fee = (total_pool * self.PLATFORM_FEE_PERCENTAGE) // 100
        prize_pool = total_pool - platform_fee

        # Determine which distribution rule to use
        for participant_threshold in sorted(self.PRIZE_DISTRIBUTION.keys()):
            if self.current_participants <= participant_threshold:
                distribution = self.PRIZE_DISTRIBUTION[participant_threshold]
                break

        # Calculate actual prize amounts
        prizes = {}
        for position, percentage in distribution:
            prize_amount = (prize_pool * percentage) // 100
            prizes[f"{position}_place"] = prize_amount

        return {
            'total_pool': total_pool,
            'platform_fee': platform_fee,
            'prize_pool': prize_pool,
            'distribution': prizes
        }

class RoomParticipant(BaseModel):
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE,
        related_name='participants'
    )
    user = models.CharField(max_length=255)  # Clerk user ID
    score = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['room', 'user']
        ordering = ['-score', 'completed_at']
