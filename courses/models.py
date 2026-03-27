from django.db import models
from django.utils import timezone
from django.conf import settings
from accounts.models import CustomUser

# ----------------------------
# Department & Program
# ----------------------------
class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Program(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programs')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# ----------------------------
# Courses & Lessons
# ----------------------------
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'lecturer'},
        related_name='courses'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class LessonMaterial(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='lesson_materials/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"


# ----------------------------
# Enrollment & Results
# ----------------------------
class Enrollment(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    lecturer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='lecturer_enrollments')
    approved = models.BooleanField(default=False)
    date_enrolled = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Automatically assign lecturer from the course if not already set
        if self.course and self.course.lecturer and not self.lecturer:
            self.lecturer = self.course.lecturer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"


class Result(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='results')
    score = models.FloatField()
    max_score = models.FloatField(default=100)
    passed = models.BooleanField(default=False)
    date_taken = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.enrollment.student.username} - {self.enrollment.course.title} - {self.score}/{self.max_score}"


# ----------------------------
# Certificates
# ----------------------------
def default_completion_date():
    return timezone.now().date()


class Certificate(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='certificate')
    completion_date = models.DateField(default=default_completion_date)
    issued = models.BooleanField(default=False)
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)

    def __str__(self):
        return f"{self.enrollment.student.username} - {self.enrollment.course.title} - {'Issued' if self.issued else 'Pending'}"


# -----------------------------
# Notifications
# -----------------------------
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
