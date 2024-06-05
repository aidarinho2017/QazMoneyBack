
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


class NoteListCreate(generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Note.objects.filter(author=user)

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(author=self.request.user)
        else:
            print(serializer.errors)


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def purchase(self, request, pk=None):
        try:
            item = self.get_object()
            user_profile = request.user.userprofile

            if user_profile.coins >= item.price:
                user_profile.coins -= item.price
                user_profile.save()
                UserItem.objects.create(user=request.user, item=item)
                return Response({'status': 'purchase successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'not enough coins'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NoteDelete(generics.DestroyAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Note.objects.filter(author=user)



class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_coins(request):
    user_profile = request.user.userprofile
    return Response({'coins': user_profile.coins})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def increment_coins(request):
    user_profile = request.user.userprofile
    user_profile.coins += 5
    user_profile.save()
    return Response({'coins': user_profile.coins})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_salary(request):
    user_profile = request.user.userprofile
    now = timezone.now()

    if user_profile.last_salary_received and (now - user_profile.last_salary_received) < timedelta(hours=1):
        next_salary_time = user_profile.last_salary_received + timedelta(hours=1)
        remaining_time = (next_salary_time - now).total_seconds()
        return Response({'error': '', 'remaining_time': remaining_time}, status=400)

    user_profile.coins += 100000 * (0.1 * user_profile.salary_got)
    user_profile.salary_got += 1
    user_profile.last_salary_received = now
    user_profile.save()
    return Response({'coins': user_profile.coins})


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class UserItemViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserItem.objects.filter(user=self.request.user)