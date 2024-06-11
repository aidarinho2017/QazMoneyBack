from django.http import JsonResponse
from django.contrib.auth.models import User
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from .models import Note, UserProfile, Item, UserItem
from .serializers import UserSerializer, NoteSerializer, ItemSerializer, UserItemSerializer
from rest_framework.decorators import api_view, permission_classes, action
from django.db.models.signals import post_save
from django.dispatch import receiver

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_money_per_hour(request):
    user_profile = request.user.userprofile
    money_per_hour = user_profile.calculate_money_per_hour()
    return Response({'money_per_hour': money_per_hour})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def collect_passive_income(request):
    user_profile = request.user.userprofile
    money_per_hour = user_profile.calculate_money_per_hour()
    user_profile.coins += money_per_hour
    user_profile.save()
    return Response({'coins': user_profile.coins})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def collect_money_per_minute(request):
    user_profile = request.user.userprofile
    now = timezone.now()

    if user_profile.last_collection_time and (now - user_profile.last_collection_time) < timedelta(minutes=1):
        next_collection_time = user_profile.last_collection_time + timedelta(minutes=1)
        remaining_time = (next_collection_time - now).total_seconds()
        return Response({'error': 'Money already collected within the last minute.', 'remaining_time': remaining_time}, status=400)

    money_per_minute = user_profile.calculate_money_per_minute()
    user_profile.coins += money_per_minute
    user_profile.last_collection_time = now
    user_profile.save()
    return Response({'coins': user_profile.coins})