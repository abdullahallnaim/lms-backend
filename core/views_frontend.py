from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from .utils.api_client import ApiClient

def home_view(request):
    """Homepage view showing featured courses and categories"""
    api_client = ApiClient(request)
    
    try:
        # Get active courses and categories from API
        courses = api_client.get_courses(is_active=True)
        categories = api_client.get_categories(is_active=True)
        
        # Use only first 6 courses for featured section
        featured_courses = courses[:6] if courses else []
        
        return render(request, 'home.html', {
            'featured_courses': featured_courses,
            'categories': categories
        })
    except Exception as e:
        messages.error(request, f"Error fetching data: {str(e)}")
        return render(request, 'home.html', {
            'featured_courses': [],
            'categories': []
        })

@login_required
def dashboard_view(request):
    """Dashboard view for users, showing different content based on user role"""
    user = request.user
    api_client = ApiClient(request)
    
    try:
        if user.role == 'admin':
            # Admin sees all users and courses stats
            courses = api_client.get_courses()
            students = api_client.get_users(role='student')
            teachers = api_client.get_users(role='teacher')
            categories = api_client.get_categories()
            
            context = {
                'total_courses': len(courses) if courses else 0,
                'total_students': len(students) if students else 0,
                'total_teachers': len(teachers) if teachers else 0,
                'total_categories': len(categories) if categories else 0,
            }
            return render(request, 'admin/dashboard.html', context)
        
        elif user.role == 'teacher':
            # Teacher sees their courses and student enrollments
            teacher_courses = api_client.get_courses()  # API should filter by current user
            all_enrollments = api_client.get_enrollments()
            
            # Filter enrollments for teacher's courses
            course_ids = [course['id'] for course in teacher_courses]
            course_enrollments = [e for e in all_enrollments if e['course_id'] in course_ids]
            
            # Count unique students
            unique_students = set(e['student_id'] for e in course_enrollments)
            
            context = {
                'courses': teacher_courses,
                'total_students': len(unique_students)
            }
            return render(request, 'teacher/dashboard.html', context)
        
        elif user.role == 'student':
            # Student sees enrolled courses and progress
            enrollments = api_client.get_enrollments(student_id=user.id)
            
            # Count completed and in-progress courses
            completed_courses = [e for e in enrollments if e['is_completed']]
            in_progress_courses = [e for e in enrollments if not e['is_completed']]
            
            context = {
                'enrollments': enrollments,
                'completed_courses': len(completed_courses),
                'in_progress_courses': len(in_progress_courses),
            }
            return render(request, 'student/dashboard.html', context)
        
        else:
            messages.error(request, "Invalid user role")
            return redirect('home')
            
    except Exception as e:
        messages.error(request, f"Error fetching dashboard data: {str(e)}")
        return redirect('home')

@login_required
def course_list_view(request):
    """View displaying all available courses with filtering options"""
    api_client = ApiClient(request)
    
    try:
        # Get categories for filter dropdown
        categories = api_client.get_categories(is_active=True)
        
        # Handle category filter
        category_id = request.GET.get('category')
        
        # Get courses with optional filter
        courses = api_client.get_courses(
            category_id=category_id if category_id else None,
            is_active=True
        )
        
        context = {
            'courses': courses,
            'categories': categories,
            'selected_category': int(category_id) if category_id else None
        }
        return render(request, 'courses/course_list.html', context)
        
    except Exception as e:
        messages.error(request, f"Error fetching courses: {str(e)}")
        return render(request, 'courses/course_list.html', {
            'courses': [],
            'categories': [],
            'selected_category': None
        })

@login_required
def course_detail_view(request, pk):
    """Detailed view for a specific course"""
    api_client = ApiClient(request)
    
    try:
        # Get course details
        course = api_client.get_course(pk)
        if not course:
            raise Http404("Course not found")
        
        # Get lessons and materials for this course
        lessons = api_client.get_lessons(course_id=pk)
        materials = api_client.get_materials(course_id=pk)
        
        # Check if user is enrolled
        is_enrolled = False
        if request.user.role == 'student':
            enrollments = api_client.get_enrollments(
                student_id=request.user.id,
                course_id=pk
            )
            is_enrolled = len(enrollments) > 0
        
        context = {
            'course': course,
            'lessons': lessons,
            'materials': materials,
            'is_enrolled': is_enrolled,
            'is_owner': request.user.id == course.get('instructor_id')
        }
        return render(request, 'courses/course_detail.html', context)
        
    except Http404:
        messages.error(request, "Course not found")
        return redirect('course_list')
    except Exception as e:
        messages.error(request, f"Error fetching course details: {str(e)}")
        return redirect('course_list')

@login_required
def category_list_view(request):
    """View displaying all course categories"""
    api_client = ApiClient(request)
    
    try:
        categories = api_client.get_categories(is_active=True)
        return render(request, 'courses/category_list.html', {
            'categories': categories
        })
    except Exception as e:
        messages.error(request, f"Error fetching categories: {str(e)}")
        return render(request, 'courses/category_list.html', {
            'categories': []
        })

@login_required
def enroll_course_view(request, course_id):
    """Handle course enrollment for students"""
    if request.user.role != 'student':
        messages.error(request, "Only students can enroll in courses")
        return redirect('course_detail', pk=course_id)
    
    api_client = ApiClient(request)
    
    try:
        # Check if already enrolled
        existing_enrollments = api_client.get_enrollments(
            student_id=request.user.id,
            course_id=course_id
        )
        
        if existing_enrollments:
            messages.info(request, "You are already enrolled in this course")
            return redirect('course_detail', pk=course_id)
        
        # Get course details to get the price
        course = api_client.get_course(course_id)
        if not course:
            messages.error(request, "Course not found")
            return redirect('course_list')
        
        # Create enrollment
        enrollment_data = {
            'student_id': request.user.id,
            'course_id': course_id,
            'price': course['price'],
            'is_active': True,
            'progress': 0,
            'is_completed': False,
            'total_mark': 0,
            'is_certificate_ready': False
        }
        
        api_client.create_enrollment(enrollment_data)
        
        messages.success(request, f"Successfully enrolled in {course['title']}")
        return redirect('my_courses')
        
    except Exception as e:
        messages.error(request, f"Error enrolling in course: {str(e)}")
        return redirect('course_detail', pk=course_id)

@login_required
def my_courses_view(request):
    """View showing enrolled courses for students"""
    if request.user.role != 'student':
        messages.error(request, "This page is for students only")
        return redirect('dashboard')
    
    api_client = ApiClient(request)
    
    try:
        # Get student enrollments
        enrollments = api_client.get_enrollments(student_id=request.user.id)
        
        # Filter by status if requested
        status = request.GET.get('status')
        if status == 'completed':
            enrollments = [e for e in enrollments if e['is_completed']]
        elif status == 'in_progress':
            enrollments = [e for e in enrollments if not e['is_completed']]
        
        return render(request, 'student/my_courses.html', {
            'enrollments': enrollments
        })
    except Exception as e:
        messages.error(request, f"Error fetching your courses: {str(e)}")
        return render(request, 'student/my_courses.html', {
            'enrollments': []
        })