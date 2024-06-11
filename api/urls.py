from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import increment_coins, get_coins, ItemViewSet, get_salary
from .views1 import get_money_per_hour, collect_passive_income, collect_money_per_minute

router = DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'user-items', views.UserItemViewSet, basename='user-items')
urlpatterns = [
    path("notes/", views.NoteListCreate.as_view(), name="note-list"),
    path("notes/delete/<int:pk>/", views.NoteDelete.as_view(), name="delete-note"),
    path('coins/', get_coins, name='get_coins'),
    path('increment/', increment_coins, name='increment_coins'),
    path('getsalary/', get_salary, name='get_salary'),
    path('', include(router.urls)),
    path('user-items/', include(router.urls)),
    path('money-per-hour/', get_money_per_hour),
    path('collect_passive_income/', collect_passive_income),
    path('collect-money-per-minute/', collect_money_per_minute)
]