from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import increment_coins, get_coins, ItemViewSet, get_salary

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
]