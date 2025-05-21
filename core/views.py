from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import Category, Course, Lesson, Material, Enrollment, QuestionAnswer
from .serializers import (
    CategorySerializer, CourseSerializer, LessonSerializer, MaterialSerializer,
    EnrollmentSerializer, QuestionAnswerSerializer
)
from drf_yasg.utils import swagger_auto_schema

# ==================== CATEGORIES ====================

@swagger_auto_schema(method='post', request_body=CategorySerializer)
@api_view(['GET', 'POST'])
def category_list_create(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if not request.user.is_authenticated or request.user.role != 'admin':
            return Response({"detail": "Only admin can create categories."}, status=403)

        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ==================== COURSES ====================

@swagger_auto_schema(method='post', request_body=CourseSerializer)
@api_view(['GET', 'POST'])
def course_list_create(request):
    if request.method == 'GET':
        category = request.query_params.get('category')
        search = request.query_params.get('search')
        queryset = Course.objects.all()

        if category:
            queryset = queryset.filter(category__id=category)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        if request.user.is_authenticated and request.user.role == 'teacher':
            queryset = queryset.filter(teacher=request.user)

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = CourseSerializer(
            paginated_queryset,
            many=True,
            context={'request': request}
        )

        return paginator.get_paginated_response(serializer.data)

    elif request.method == 'POST':
        if not request.user.is_authenticated or request.user.role != 'teacher':
            return Response({'detail': 'Only teachers can create courses.'}, status=403)

        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='put', request_body=CourseSerializer)
@api_view(['GET', 'PUT', 'DELETE'])
def course_detail(request, pk):
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'detail': 'Course not found'}, status=404)

    if request.method == 'GET':
        is_owner = request.user.is_authenticated and request.user == course.teacher
        is_admin = request.user.is_authenticated and request.user.role == 'admin'
        is_enrolled = Enrollment.objects.filter(
            student=request.user,
            course=course,
            status='active'
        ).exists() if request.user.is_authenticated and request.user.role == 'student' else False

        if not (is_owner or is_admin or is_enrolled):
            serializer = CourseSerializer(course, context={'limited': True})
        else:
            serializer = CourseSerializer(course, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'PUT':
        if not request.user.is_authenticated or request.user.role != 'teacher' or request.user != course.teacher:
            return Response({'detail': 'Only the course owner can update this course.'}, status=403)

        serializer = CourseSerializer(course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not request.user.is_authenticated or request.user.role != 'teacher' or request.user != course.teacher:
            return Response({'detail': 'Only the course owner can delete this course.'}, status=403)

        course.delete()
        return Response({'detail': 'Course deleted'}, status=status.HTTP_204_NO_CONTENT)

# ==================== LESSONS ====================

@swagger_auto_schema(method='post', request_body=LessonSerializer)
@api_view(['GET', 'POST'])
def lesson_list_create(request):
    if request.method == 'GET':
        course = request.query_params.get('course')
        if not course:
            return Response({'detail': 'Course ID is required'}, status=400)

        try:
            course = Course.objects.get(pk=course)
        except Course.DoesNotExist:
            return Response({'detail': 'Course not found'}, status=404)

        is_teacher = request.user.is_authenticated and request.user.role == 'teacher' and request.user == course.teacher
        is_admin = request.user.is_authenticated and request.user.role == 'admin'
        is_enrolled = Enrollment.objects.filter(
            student=request.user,
            course=course,
            status='active'
        ).exists() if request.user.is_authenticated and request.user.role == 'student' else False

        if not (is_teacher or is_admin or is_enrolled):
            return Response({'detail': 'You do not have permission to view these lessons'}, status=403)

        lessons = Lesson.objects.filter(course=course).order_by('order')
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if not request.user.is_authenticated or request.user.role != 'teacher':
            return Response({'detail': 'Only teachers can create lessons'}, status=403)

        course = request.data.get('course')
        try:
            course = Course.objects.get(pk=course)
        except Course.DoesNotExist:
            return Response({'detail': 'Course not found'}, status=404)

        if request.user != course.teacher:
            return Response({'detail': 'You can only add lessons to your own courses'}, status=403)

        serializer = LessonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='put', request_body=LessonSerializer)
@api_view(['GET', 'PUT', 'DELETE'])
def lesson_detail(request, pk):
    try:
        lesson = Lesson.objects.get(pk=pk)
    except Lesson.DoesNotExist:
        return Response({'detail': 'Lesson not found'}, status=404)

    if request.method == 'GET':
        course = lesson.course
        is_teacher = request.user.is_authenticated and request.user.role == 'teacher' and request.user == course.teacher
        is_admin = request.user.is_authenticated and request.user.role == 'admin'
        is_enrolled = Enrollment.objects.filter(
            student=request.user,
            course=course,
            status='active'
        ).exists() if request.user.is_authenticated and request.user.role == 'student' else False

        if not (is_teacher or is_admin or is_enrolled):
            return Response({'detail': 'You do not have permission to view this lesson'}, status=403)

        serializer = LessonSerializer(lesson)
        return Response(serializer.data)

    elif request.method == 'PUT':
        if not request.user.is_authenticated or request.user.role != 'teacher' or request.user != lesson.course.teacher:
            return Response({'detail': 'Only the course owner can update this lesson'}, status=403)

        serializer = LessonSerializer(lesson, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not request.user.is_authenticated or request.user.role != 'teacher' or request.user != lesson.course.teacher:
            return Response({'detail': 'Only the course owner can delete this lesson'}, status=403)

        lesson.delete()
        return Response({'detail': 'Lesson deleted'}, status=status.HTTP_204_NO_CONTENT)
    
# ==================== MATERIALS ====================

@swagger_auto_schema(method='post', request_body=MaterialSerializer)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def material_list_create(request):
    if request.method == 'GET':
        lesson = request.query_params.get('lesson')
        if not lesson:
            return Response({'detail': 'Lesson ID is required'}, status=400)

        try:
            lesson = Lesson.objects.get(pk=lesson)
        except Lesson.DoesNotExist:
            return Response({'detail': 'Lesson not found'}, status=404)

        course = lesson.course
        is_teacher = request.user.role == 'teacher' and request.user == course.teacher
        is_admin = request.user.role == 'admin'
        is_enrolled = Enrollment.objects.filter(
            student=request.user, 
            course=course, 
            status='active'
        ).exists() if request.user.role == 'student' else False

        if not (is_teacher or is_admin or is_enrolled):
            return Response({'detail': 'You do not have permission to view these materials'}, status=403)

        materials = Material.objects.filter(lesson=lesson)
        serializer = MaterialSerializer(materials, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if request.user.role != 'teacher':
            return Response({'detail': 'Only teachers can upload materials'}, status=403)

        lesson = request.data.get('lesson')
        try:
            lesson = Lesson.objects.get(pk=lesson)
        except Lesson.DoesNotExist:
            return Response({'detail': 'Lesson not found'}, status=404)

        if request.user != lesson.course.teacher:
            return Response({'detail': 'You can only add materials to your own courses'}, status=403)

        serializer = MaterialSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='put', request_body=MaterialSerializer)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def material_detail(request, pk):
    try:
        material = Material.objects.get(pk=pk)
    except Material.DoesNotExist:
        return Response({'detail': 'Material not found'}, status=404)

    if request.method == 'GET':
        lesson = material.lesson
        course = lesson.course
        is_teacher = request.user.role == 'teacher' and request.user == course.teacher
        is_admin = request.user.role == 'admin'
        is_enrolled = Enrollment.objects.filter(
            student=request.user, 
            course=course, 
            status='active'
        ).exists() if request.user.role == 'student' else False

        if not (is_teacher or is_admin or is_enrolled):
            return Response({'detail': 'You do not have permission to view this material'}, status=403)

        serializer = MaterialSerializer(material)
        return Response(serializer.data)

    elif request.method == 'PUT':
        if request.user.role != 'teacher' or request.user != material.lesson.course.teacher:
            return Response({'detail': 'Only the course owner can update this material'}, status=403)

        serializer = MaterialSerializer(material, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if request.user.role != 'teacher' or request.user != material.lesson.course.teacher:
            return Response({'detail': 'Only the course owner can delete this material'}, status=403)

        material.delete()
        return Response({'detail': 'Material deleted'}, status=status.HTTP_204_NO_CONTENT)

# ==================== ENROLLMENTS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def enrollment_list(request):
    if request.user.role == 'teacher':
        course = request.query_params.get('course')
        if not course:
            return Response({'detail': 'Course ID is required'}, status=400)

        try:
            course = Course.objects.get(pk=course)
        except Course.DoesNotExist:
            return Response({'detail': 'Course not found'}, status=404)

        if request.user != course.teacher:
            return Response({'detail': 'You can only view enrollments for your own courses'}, status=403)

        enrollments = Enrollment.objects.filter(course=course)
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)

    elif request.user.role == 'student':
        enrollments = Enrollment.objects.filter(student=request.user)
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)

    elif request.user.role == 'admin':
        course = request.query_params.get('course')
        student = request.query_params.get('student')

        queryset = Enrollment.objects.all()

        if course:
            queryset = queryset.filter(course__id=course)
        if student:
            queryset = queryset.filter(student__id=student)

        serializer = EnrollmentSerializer(queryset, many=True)
        return Response(serializer.data)

    return Response({'detail': 'Unauthorized role'}, status=403)

@swagger_auto_schema(method='post', request_body=EnrollmentSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_course(request):
    if request.user.role != 'student':
        return Response({'detail': 'Only students can enroll in courses'}, status=403)

    course = request.data.get('course')
    payment_method = request.data.get('payment_method', 'free')

    try:
        course = Course.objects.get(pk=course)
    except Course.DoesNotExist:
        return Response({'detail': 'Course not found'}, status=404)

    if Enrollment.objects.filter(student=request.user, course=course).exists():
        return Response({'detail': 'You are already enrolled in this course'}, status=400)

    enrollment = Enrollment.objects.create(
        student=request.user,
        course=course,
        payment_method=payment_method,
        status='active'
    )

    serializer = EnrollmentSerializer(enrollment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# ==================== QUESTIONS & ANSWERS ====================

@swagger_auto_schema(method='post', request_body=QuestionAnswerSerializer)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def question_list_create(request):
    lesson = request.query_params.get('lesson')

    if request.method == 'GET':
        if not lesson:
            return Response({'detail': 'Lesson ID is required'}, status=400)

        try:
            lesson = Lesson.objects.get(pk=lesson)
        except Lesson.DoesNotExist:
            return Response({'detail': 'Lesson not found'}, status=404)

        course = lesson.course
        is_teacher = request.user.role == 'teacher' and request.user == course.teacher
        is_admin = request.user.role == 'admin'
        is_enrolled = Enrollment.objects.filter(
            student=request.user,
            course=course,
            status='active'
        ).exists() if request.user.role == 'student' else False

        if not (is_teacher or is_admin or is_enrolled):
            return Response({'detail': 'You do not have permission to view these questions'}, status=403)

        questions = QuestionAnswer.objects.filter(lesson=lesson)
        serializer = QuestionAnswerSerializer(questions, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if request.user.role != 'student':
            return Response({'detail': 'Only students can ask questions'}, status=403)

        lesson = request.data.get('lesson')
        try:
            lesson = Lesson.objects.get(pk=lesson)
        except Lesson.DoesNotExist:
            return Response({'detail': 'Lesson not found'}, status=404)

        if not Enrollment.objects.filter(
            student=request.user,
            course=lesson.course,
            status='active'
        ).exists():
            return Response({'detail': 'You are not enrolled in this course'}, status=403)

        serializer = QuestionAnswerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='put', request_body=QuestionAnswerSerializer)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def question_detail(request, pk):
    try:
        question = QuestionAnswer.objects.get(pk=pk)
    except QuestionAnswer.DoesNotExist:
        return Response({'detail': 'Question not found'}, status=404)

    if request.method == 'GET':
        lesson = question.lesson
        course = lesson.course
        is_teacher = request.user.role == 'teacher' and request.user == course.teacher
        is_admin = request.user.role == 'admin'
        is_enrolled = Enrollment.objects.filter(
            student=request.user,
            course=course,
            status='active'
        ).exists() if request.user.role == 'student' else False
        is_asker = request.user == question.student

        if not (is_teacher or is_admin or is_enrolled or is_asker):
            return Response({'detail': 'You do not have permission to view this question'}, status=403)

        serializer = QuestionAnswerSerializer(question)
        return Response(serializer.data)

    elif request.method == 'PUT':
        is_asker = request.user == question.student
        is_teacher = request.user.role == 'teacher' and request.user == question.lesson.course.teacher

        if not (is_asker or is_teacher):
            return Response({'detail': 'You do not have permission to update this question'}, status=403)

        if is_asker and not is_teacher:
            partial_data = {'question': request.data.get('question')}
            serializer = QuestionAnswerSerializer(question, data=partial_data, partial=True)
        elif is_teacher and not is_asker:
            partial_data = {'answer': request.data.get('answer')}
            serializer = QuestionAnswerSerializer(question, data=partial_data, partial=True)
        else:
            serializer = QuestionAnswerSerializer(question, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        is_asker = request.user == question.student
        is_teacher = request.user.role == 'teacher' and request.user == question.lesson.course.teacher
        is_admin = request.user.role == 'admin'

        if not (is_asker or is_teacher or is_admin):
            return Response({'detail': 'You do not have permission to delete this question'}, status=403)

        question.delete()
        return Response({'detail': 'Question deleted'}, status=status.HTTP_204_NO_CONTENT)
