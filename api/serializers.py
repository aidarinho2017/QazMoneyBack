from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Note, Item, UserItem, Category


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        print(validated_data)
        user = User.objects.create_user(**validated_data)
        return user

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

from rest_framework import serializers
from .models import Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('id', 'name', 'price', 'selling_price', 'description', 'money_per_hour', 'happiness', 'category')


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "title", "content", "created_at", "author"]
        extra_kwargs = {"author": {"read_only": True}}
class UserItemSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    item_description = serializers.ReadOnlyField(source='item.description')
    item_price = serializers.ReadOnlyField(source='item.price')
    selling_price = serializers.IntegerField(source='item.selling_price')

    class Meta:
        model = UserItem
        fields = ['id', 'item_name', 'item_description', 'item_price', 'purchased_at', 'selling_price']
