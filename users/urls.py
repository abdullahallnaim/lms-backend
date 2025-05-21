from django.urls import path
from .views import user_list_create

urlpatterns = [
    path('auth/', user_list_create, name="user_list_create"),
]
