from django.urls import path
from . import views

urlpatterns = [
    # Category endpoints
    path('categories/', views.category_list_create, name='category_list_create'),
    
    # Course endpoints
    path('courses/', views.course_list_create, name='course_list_create'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    
    # Lesson endpoints
    path('lessons/', views.lesson_list_create, name='lesson_list_create'),
    path('lessons/<int:pk>/', views.lesson_detail, name='lesson_detail'),
    
    # Material endpoints
    path('materials/', views.material_list_create, name='material_list_create'),
    path('materials/<int:pk>/', views.material_detail, name='material_detail'),
    
    # Enrollment endpoints
    path('enrollments/', views.enrollment_list, name='enrollment_list'),
    path('enrollments/enroll/', views.enroll_course, name='enroll_course'),
    
    # Question & Answer endpoints
    path('questions/', views.question_list_create, name='question_list_create'),
    path('questions/<int:pk>/', views.question_detail, name='question_detail'),
]