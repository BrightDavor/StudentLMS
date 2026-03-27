from django.urls import path
from . import views

urlpatterns = [
    # -----------------------------
    # Student Routes
    # -----------------------------
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll-course'),
    path('my-courses/', views.student_courses, name='student-courses'),
    path('add-course/', views.add_course, name='add-course'),
    path('approve-enrollment/', views.approve_enrollment, name='approve-enrollment'),

    # -----------------------------
    # API Endpoints
    # -----------------------------
    path('api/programs/<int:dept_id>/', views.api_programs, name='api-programs'),
    path('api/courses/<int:prog_id>/', views.api_courses, name='api-courses'),

    # -----------------------------
    # Lecturer Routes
    # -----------------------------
    # path('lecturer-dashboard/', views.lecturer_dashboard, name='lecturer-dashboard'),
    path('create-course/', views.create_course, name='create-course'),
    path('course/<int:course_id>/add-lesson/', views.add_lesson, name='add-lesson'),
    path('course/<int:course_id>/students/', views.view_students, name='view-students'),
    #path('lecturer-profile/', views.lecturer_profile, name='lecturer-profile'),

    # -----------------------------
    # Lesson Management
    # -----------------------------
    path('lesson/<int:lesson_id>/edit/', views.edit_lesson, name='edit-lesson'),
    path('lesson/<int:lesson_id>/delete/', views.delete_lesson, name='delete-lesson'),

    # -----------------------------
    # Course Views
    # -----------------------------
    path('all/', views.all_courses, name='all-courses'),
    path('course/<int:course_id>/', views.course_detail, name='course-detail'),  # ✅ Fixed missing route
    path('course/<int:course_id>/existing-lessons/', views.existing_lessons, name='existing-lessons'),
    path('course/<int:course_id>/students/', views.lecturer_view_students, name='lecturer-view-students'),
]
