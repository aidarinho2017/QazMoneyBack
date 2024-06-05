from django.contrib import admin
from .models import UserProfile, Note, Item, UserItem

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Note)
admin.site.register(Item)
admin.site.register(UserItem)