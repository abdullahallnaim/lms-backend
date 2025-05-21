from django.urls import path
from .views import user_list_create, student_profile, teacher_profile,forget_password,password_reset_confirm

urlpatterns = [
    path('auth/', user_list_create, name="user_list_create"),
    path('profile/student/', student_profile, name='student_profile'),
    path('profile/teacher/', teacher_profile, name='teacher_profile'),
    path('forget-password/', forget_password, name='forget_password'),
        path('reset-password/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),

]
