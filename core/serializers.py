from rest_framework import serializers
from .models import Category, Course, Lesson, Material, Enrollment, QuestionAnswer
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    category_details = CategorySerializer(source='category', read_only=True)
    instructor_details = UserSerializer(source='instructor', read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'banner', 'price', 'duration', 'is_active',
            'category', 'category_details',
            'instructor', 'instructor_details',
            'created_at', 'updated_at'
        ]


class LessonSerializer(serializers.ModelSerializer):
    course_details = CourseSerializer(source='course', read_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'video', 'is_active',
            'course', 'course_details', 'created_at', 'updated_at'
        ]

class MaterialSerializer(serializers.ModelSerializer):
    course_details = CourseSerializer(source='course', read_only=True)

    class Meta:
        model = Material
        fields = [
            'id', 'title', 'description', 'file_type', 'file', 'is_active',
            'course', 'course_details', 'created_at', 'updated_at'
        ]

class EnrollmentSerializer(serializers.ModelSerializer):
    student_details = UserSerializer(source='student', read_only=True)
    course_details = CourseSerializer(source='course', read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'student_details',
            'course', 'course_details',
            'is_active', 'price', 'progress', 'is_completed',
            'total_mark', 'is_certificate_ready', 'created_at', 'updated_at'
        ]

class QuestionAnswerSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    lesson_details = LessonSerializer(source='lesson', read_only=True)

    class Meta:
        model = QuestionAnswer
        fields = [
            'id', 'user', 'user_details',
            'lesson', 'lesson_details',
            'description', 'is_active', 'created_at', 'updated_at'
        ]