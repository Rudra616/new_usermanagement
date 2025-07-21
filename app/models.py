from django.db import models
import uuid
from django.contrib.auth.hashers import make_password

class State(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class District(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class User(models.Model):
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    userName = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=254)
    email = models.EmailField(max_length=254)
    role = models.CharField(max_length=50, default='user')
    address = models.CharField(max_length=255)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    phoneNumber = models.CharField(max_length=15, null=True, blank=True)
    dateOfBirth = models.DateField(null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    email_verification_token = models.UUIDField(default=uuid.uuid4, unique=True, null=True, blank=True)
    reset_token = models.UUIDField(null=True, blank=True)
    reset_expire = models.DateTimeField(null=True, blank=True)
    is_varified =models.BooleanField(default=False)
    def __str__(self):
        return self.userName
    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)