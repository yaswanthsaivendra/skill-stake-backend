# Generated by Django 5.1.4 on 2025-01-11 11:26

import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('creator', models.CharField(max_length=255)),
                ('current_participants', models.PositiveIntegerField(default=1)),
                ('entry_fee', models.PositiveIntegerField(help_text='Minimum entry fee is ₹100', validators=[django.core.validators.MinValueValidator(100)])),
                ('difficulty_level', models.CharField(choices=[('EASY', 'Easy'), ('MEDIUM', 'Medium'), ('HARD', 'Hard'), ('VERY_HARD', 'Very Hard')], default='MEDIUM', max_length=10)),
                ('scheduled_start_time', models.DateTimeField()),
                ('registration_deadline', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed')], default='PENDING', max_length=20)),
                ('duration_minutes', models.PositiveIntegerField(default=30, help_text='Duration of the game in minutes')),
                ('started_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-scheduled_start_time'],
            },
        ),
        migrations.CreateModel(
            name='RoomParticipant',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.CharField(max_length=255)),
                ('score', models.IntegerField(default=0)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='rooms.room')),
            ],
            options={
                'ordering': ['-score', 'completed_at'],
                'unique_together': {('room', 'user')},
            },
        ),
    ]
