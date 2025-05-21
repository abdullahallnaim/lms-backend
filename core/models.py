from django.db import models
from users.models import User
# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    banner = models.ImageField(upload_to='course_banners/')
    price = models.FloatField()
    duration = models.FloatField()
    is_active = models.BooleanField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role' : 'teacher'})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    video = models.FileField(upload_to='lesson_videoes')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Material(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    file_type= models.CharField(max_length=100)
    file = models.FileField(upload_to='materials/')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role' : 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    price = models.FloatField()
    progress = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    total_mark = models.FloatField(default=0)
    is_certificate_ready = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

class QuestionAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} --> {self.lesson.title} --> {self.description}"
    