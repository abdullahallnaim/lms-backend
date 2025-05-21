import requests
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

class ApiClient:
    """
    Utility class for making API requests to the LMS backend
    """
    
    def __init__(self, request=None):
        """
        Initialize the API client with the request object
        to extract authentication tokens if available
        """
        self.base_url = f"{settings.API_BASE_URL}/api"
        self.headers = {
            'Content-Type': 'application/json',
        }
        
        # Add authentication token if user is logged in
        if request and request.user and not isinstance(request.user, AnonymousUser):
            self.headers['Authorization'] = f"Bearer {self._get_auth_token(request)}"
    
    def _get_auth_token(self, request):
        """Get authentication token from session or user model"""
        # In a real implementation, you would use your actual token mechanism
        # For this example, we'll assume a simple token attribute on the user
        return getattr(request.user, 'auth_token', None)
    
    def _make_request(self, method, endpoint, data=None, params=None):
        """Make HTTP request to the API endpoint"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            if method.lower() == 'get':
                response = requests.get(url, headers=self.headers, params=params)
            elif method.lower() == 'post':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.lower() == 'put':
                response = requests.put(url, headers=self.headers, json=data)
            elif method.lower() == 'delete':
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            return response.json() if response.content else None
            
        except requests.exceptions.RequestException as e:
            # Log error and re-raise or handle as needed
            print(f"API request error: {e}")
            raise
    
    # Category endpoints
    def get_categories(self, is_active=None):
        """Get all categories, optionally filtered by is_active"""
        params = {}
        if is_active is not None:
            params['is_active'] = is_active
        return self._make_request('get', '/courses/categories/', params=params)
    
    def create_category(self, data):
        """Create a new category"""
        return self._make_request('post', '/courses/categories/', data=data)
    
    # Course endpoints
    def get_courses(self, category=None, is_active=None):
        """Get all courses with optional filtering"""
        params = {}
        if category:
            params['category'] = category
        if is_active is not None:
            params['is_active'] = is_active
        return self._make_request('get', '/courses/courses/', params=params)
    
    def get_course(self, course):
        """Get a specific course by ID"""
        return self._make_request('get', f'/courses/courses/{course}/')
    
    def create_course(self, data):
        """Create a new course"""
        return self._make_request('post', '/courses/courses/', data=data)
    
    def update_course(self, course, data):
        """Update an existing course"""
        return self._make_request('put', f'/courses/courses/{course}/', data=data)
    
    def delete_course(self, course):
        """Delete a course"""
        return self._make_request('delete', f'/courses/courses/{course}/')
    
    # Lesson endpoints
    def get_lessons(self, course=None):
        """Get lessons, optionally filtered by course"""
        params = {}
        if course:
            params['course'] = course
        return self._make_request('get', '/courses/lessons/', params=params)
    
    def create_lesson(self, data):
        """Create a new lesson"""
        return self._make_request('post', '/courses/lessons/', data=data)
    
    # Material endpoints
    def get_materials(self, course=None):
        """Get materials, optionally filtered by course"""
        params = {}
        if course:
            params['course'] = course
        return self._make_request('get', '/courses/materials/', params=params)
    
    def create_material(self, data):
        """Create a new material"""
        return self._make_request('post', '/courses/materials/', data=data)
    
    # Enrollment endpoints
    def get_enrollments(self, student=None, course=None):
        """Get enrollments, optionally filtered by student or course"""
        params = {}
        if student:
            params['student'] = student
        if course:
            params['course'] = course
        return self._make_request('get', '/courses/enrollments/', params=params)
    
    def create_enrollment(self, data):
        """Create a new enrollment"""
        return self._make_request('post', '/courses/enrollments/', data=data)
    
    def update_enrollment(self, enrollment_id, data):
        """Update an enrollment (e.g., progress)"""
        return self._make_request('put', f'/courses/enrollments/{enrollment_id}/', data=data)
    
    # Question/Answer endpoints
    def get_questions(self, lesson=None, user=None):
        """Get questions, optionally filtered by lesson or user"""
        params = {}
        if lesson:
            params['lesson'] = lesson
        if user:
            params['user'] = user
        return self._make_request('get', '/courses/questions/', params=params)
    
    def create_question(self, data):
        """Create a new question"""
        return self._make_request('post', '/courses/questions/', data=data)
    
    # User endpoints
    def get_users(self, role=None):
        """Get users, optionally filtered by role"""
        params = {}
        if role:
            params['role'] = role
        return self._make_request('get', '/users/auth/', params=params)
    
    def create_user(self, data):
        """Create a new user"""
        return self._make_request('post', '/users/auth/', data=data)