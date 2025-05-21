from django.db import models
from django.contrib.auth.models import AbstractUser

USER_ROLES = (
    ('admin', 'admin'),
    ('teacher', 'Teacher'),
    ('student', 'Student'),
)

class User(AbstractUser):
    role = models.CharField(max_length=10, choices=USER_ROLES)
    mobile_no = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"