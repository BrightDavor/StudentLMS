from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, user_type='student', **extra_fields):
        """
        Creates and saves a user with the given email, username, password, and user_type.
        """
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            user_type=user_type,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Creates and saves a superuser (admin)
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # ✅ Pass user_type manually here
        user = self.create_user(email, username, password=password, **extra_fields)
        user.user_type = 'admin'
        user.save(using=self._db)
        return user


from django.utils import timezone

class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('lecturer', 'Lecturer'),
        ('student', 'Student'),
        ('learner', 'Learner'),
    )

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)
    date_joined = models.DateTimeField(default=timezone.now)   # ✅ Add this

    # Extended fields...
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    region = models.CharField(max_length=50, blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    nationality = models.CharField(max_length=50, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    theme = models.CharField(max_length=10, default='light')  # light or dark
    language = models.CharField(max_length=20, default='English')
    bio = models.TextField(blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'user_type']

    def __str__(self):
        return f"{self.username} ({self.user_type})"


    @property
    def is_online(self):
        """Check if user is online (active within last 60 seconds)"""
        return (timezone.now() - self.last_seen).seconds < 60

    # Optional: helper to check user type
    def is_student(self):
        return self.user_type == 'student'

    def is_lecturer(self):
        return self.user_type == 'lecturer'

    def is_admin(self):
        return self.user_type == 'admin'
