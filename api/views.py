from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from .models import Note, UserProfile, Item, UserItem, Category
from .serializers import UserSerializer, NoteSerializer, ItemSerializer, UserItemSerializer, CategorySerializer
from rest_framework.decorators import api_view, permission_classes, action
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render, reverse
from .models import ChatBot
from django.http import HttpResponseRedirect, JsonResponse
import google.generativeai as genai

genai.configure(api_key="AIzaSyChvLXJCiZ1f2p71qjtWdtrLeuUXoofmh8")

@csrf_exempt
def ask_question(request):
    if request.method == "POST":
        text = request.POST.get("text")
        model = genai.GenerativeModel('gemini-1.5-flash')
        chat = model.start_chat()
        response = chat.send_message(text)
        user = request.user
        ChatBot.objects.create(text_input=text, gemini_output=response.text, user=user)

        response_data = {
            "text": response.text,
        }
        return JsonResponse({"data": response_data})
    else:
        return JsonResponse({"error": "Invalid method"}, status=400)

def get_chats(request):
    user = request.user
    chats = ChatBot.objects.filter(user=user)
    chat_data = [{"text_input": chat.text_input, "gemini_output": chat.gemini_output, "date": chat.date} for chat in chats]
    return JsonResponse({"chats": chat_data})

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_coins(request):
    user_profile = request.user.userprofile
    return Response({'coins': user_profile.coins})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_happiness(request):
    user_profile = request.user.userprofile
    return Response({'happiness': user_profile.happiness})

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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def sell(self, request, pk=None):
        try:
            user_item = self.get_object()
            item = user_item.item
            user_profile = request.user.userprofile
            user_profile.coins += item.selling_price
            user_profile.happiness -= item.happiness
            user_profile.save()

            user_item.delete()
            return Response({
                'status': 'sell successful',
                'coins': user_profile.coins,
                'happiness': user_profile.happiness
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

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
                user_profile.happiness += item.happiness
                user_profile.save()
                UserItem.objects.create(user=request.user, item=item)
                return Response({'status': 'purchase successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'not enough coins'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def by_category(self, request):
        category_id = request.query_params.get('category')
        if category_id:
            items = Item.objects.filter(category_id=category_id)
        else:
            items = Item.objects.all()
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)


class NoteDelete(generics.DestroyAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Note.objects.filter(author=user)