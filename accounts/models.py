# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("doctor", "Doctor"),
        ("nurse", "Nurse"),
        ("patient", "Patient"),
        ("admin", "Admin"),
    )
    username = models.CharField(
        max_length=150, unique=True, blank=False, null=False
    )
    email = models.EmailField(
        max_length=254, unique=True, blank=True, null=False
    )   
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=False, null=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="patient")
    is_doctor = models.BooleanField(default=False)
    department = models.CharField(max_length=100, blank=True, null=True)
    specialty = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", blank=True, null=True
    )
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.username
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = generate_username(self.first_name, self.last_name)
        super().save(*args, **kwargs)
        
def generate_username(first_name, last_name):
    base_username = (first_name + last_name).lower().replace(" ", "")
    random_digits = ''.join(random.choices(string.digits, k=5))
    return f"{base_username}{random_digits}"