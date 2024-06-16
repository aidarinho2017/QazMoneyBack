from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Note(models.Model):
    title = models.CharField(max_length=60)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    coins = models.PositiveIntegerField(default=0)
    last_salary_received = models.DateTimeField(null=True, blank=True)
    salary_got = models.IntegerField(default=1)
    happiness = models.PositiveIntegerField(default=0)
    last_collection_time = models.DateTimeField(null=True, blank=True)  # New field

    def __str__(self):
        return f"{self.user.username} - {self.coins} coins"

    def calculate_money_per_hour(self):
        user_items = UserItem.objects.filter(user=self.user)
        total_money_per_hour = sum(item.item.money_per_hour for item in user_items)
        return total_money_per_hour

    def calculate_money_per_minute(self):
        return self.calculate_money_per_hour() / 60

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    selling_price = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    money_per_hour = models.IntegerField(default=0)
    happiness = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name
class UserItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)
    money_per_hour_at_purchase = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.user.username} - {self.item.name}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.money_per_hour_at_purchase = self.item.money_per_hour
        super().save(*args, **kwargs)

class ChatBot(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="GeminiUser", null=True
    )
    text_input = models.CharField(max_length=500)
    gemini_output = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.text_input