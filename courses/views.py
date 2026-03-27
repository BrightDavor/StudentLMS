from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Department, Program, Course, Enrollment, Lesson, LessonMaterial
from .forms import EnrollmentForm
from .forms import CourseForm, LessonForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from datetime import datetime

# -----------------------------
# Course Detail & Enrollment
# -----------------------------
def existing_lessons(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    # Add more context if needed
    return render(request, 'courses/existing_lessons.html', {'course': course})

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Check if student is already enrolled
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        # Optional: add a message if already enrolled
        # messages.info(request, "You are already enrolled in this course.")
        return redirect('student-courses')

    # Assign lecturer from the course
    lecturer = course.lecturer  # This assumes your Course model has a ForeignKey to the lecturer

    # Create enrollment and assign lecturer
    Enrollment.objects.create(
        student=request.user,
        course=course,
        lecturer=lecturer,  # make sure your Enrollment model has a lecturer field
        approved=False  # initially pending approval
    )

    # Optional: Add a message
    # messages.success(request, f"You have successfully enrolled in {course.title}.")

    return redirect('student-courses')

# -----------------------------
# Department & Program Selection
# -----------------------------
@login_required
def choose_program(request):
    departments = Department.objects.all()
    return render(request, 'courses/choose_program.html', {'departments': departments})

@login_required
def program_courses(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    programs = department.program_set.all()
    return render(request, 'courses/program_courses.html', {'department': department, 'programs': programs})

@login_required
def course_list(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    courses = program.course_set.all()
    return render(request, 'courses/course_list.html', {'program': program, 'courses': courses})

# -----------------------------
# API Endpoints
# -----------------------------
@login_required
def api_programs(request, dept_id):
    programs = Program.objects.filter(department_id=dept_id)
    data = [{'id': p.id, 'name': p.name} for p in programs]
    return JsonResponse(data, safe=False)

@login_required
def api_courses(request, prog_id):
    courses = Course.objects.filter(program_id=prog_id)
    data = [{'id': c.id, 'title': c.title} for c in courses]
    return JsonResponse(data, safe=False)

# -----------------------------
# Student Dashboard
# -----------------------------
@login_required
def student_dashboard(request):
    if request.user.user_type != 'student':
        return redirect('home')

    enrollments = Enrollment.objects.filter(user=request.user)
    approved_courses = [e.course for e in enrollments if e.approved]
    pending_courses = [e.course for e in enrollments if not e.approved]

    return render(request, 'accounts/student_dashboard.html', {
        'student': request.user,
        'approved_courses': approved_courses,
        'pending_courses': pending_courses,
    })


def course_detail(request, course_id):
    # Get the course
    course = get_object_or_404(Course, id=course_id)
    
    # Get all lessons for this course
    lessons = Lesson.objects.filter(course=course).order_by('id')
    
    # Get lecturer from the course
    lecturer = course.lecturer if hasattr(course, 'lecturer') else None

    context = {
        'course': course,
        'lessons': lessons,
        'lecturer': lecturer,  # <-- Make sure this is passed
    }
    
    return render(request, 'courses/course_detail.html', context)

# Student Courses Page
# -----------------------------
@login_required
def student_courses(request):
    """
    Displays all courses the current student is enrolled in.
    """
    from courses.models import Enrollment  # import here to avoid circular imports
    enrollments = Enrollment.objects.filter(student=request.user)

    context = {
        'enrollments': enrollments,
        'student': request.user
    }
    return render(request, 'accounts/student_courses.html', context)
# -----------------------------
# Add Course (Pending Approval)
# -----------------------------
@login_required
def add_course(request):
    if request.user.user_type != 'student':
        return redirect('home')

    # ✅ Use 'student' instead of 'user'
    existing_courses = Enrollment.objects.filter(student=request.user).values_list('course_id', flat=True)
    available_courses = Course.objects.exclude(id__in=existing_courses)

    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course']
            # ✅ Use 'student' instead of 'user'
            Enrollment.objects.get_or_create(student=request.user, course=course, approved=False)
            return redirect('student-courses')
    else:
        form = EnrollmentForm()

    return render(request, 'courses/add_course.html', {
        'form': form,
        'available_courses': available_courses
    })

# -----------------------------
# Admin: Approve Enrollment
# -----------------------------
@staff_member_required
def approve_enrollment(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    enrollment.approved = True
    enrollment.save()
    return redirect('admin:courses_enrollment_changelist')

@login_required
def approve_enrollment(request):
    if request.method == 'POST':
        enrollment_id = request.POST.get('enrollment_id')
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id)
            enrollment.approved = True
            enrollment.save()
            return JsonResponse({'success': True})
        except Enrollment.DoesNotExist:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False})


#lecturers
@login_required
def lecturer_dashboard(request):
    courses = Course.objects.filter(lecturer=request.user)
    return render(request, 'courses/lecturer_dashboard.html', {'courses': courses})

# Create a new course

def create_course(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        program_id = request.POST.get('program')

        program = get_object_or_404(Program, id=program_id)

        Course.objects.create(
            title=title,
            description=description,
            program=program,
            lecturer=request.user
        )
        return redirect('lecturer-dashboard')

    programs = Program.objects.all()
    return render(request, 'courses/create_course.html', {'programs': programs})

# Add lesson to a course
def add_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = Lesson.objects.filter(course=course)

    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            # Save the lesson
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()

            # Handle multiple uploaded files
            files = request.FILES.getlist('files')
            for f in files:
                LessonMaterial.objects.create(
                    lesson=lesson,
                    title=f.name,
                    file=f
                )

            messages.success(request, "Lesson and materials added successfully!")
            return redirect('existing-lessons', course_id=course.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LessonForm()

    context = {
        'form': form,
        'lessons': lessons,
        'course': course
    }
    return render(request, 'courses/add_lesson.html', context)

# View enrolled students
@login_required
def view_students(request, course_id):
    course = get_object_or_404(Course, id=course_id, lecturer=request.user)
    enrollments = course.enrollments.all()  # ✅ Uses related_name
    students = [enrollment.student for enrollment in enrollments]

    return render(request, 'courses/view_students.html', {
        'course': course,
        'students': students
    })

def lecturer_view_students(request, course_id):
    # Get the course or 404
    course = get_object_or_404(Course, id=course_id)

    # Get all students enrolled in this course
    enrollments = Enrollment.objects.filter(course=course)
    students = []

    for enrollment in enrollments:
        student = enrollment.student
        # Add a safe URL for profile picture
        if student.profile_picture:
            student.profile_picture_url = student.profile_picture.url
        else:
            student.profile_picture_url = '/static/images/default-profile.png'  # make sure this exists
        students.append(student)

    context = {
        'course': course,
        'students': students
    }
    return render(request, 'courses/view_students.html', context)

# Edit a lesson
def edit_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()

            # Add new materials if uploaded
            files = request.FILES.getlist('files')
            for f in files:
                LessonMaterial.objects.create(
                    lesson=lesson,
                    title=f.name,
                    file=f
                )

            messages.success(request, "Lesson updated successfully!")
            return redirect('existing-lessons', course_id=course.id)
    else:
        form = LessonForm(instance=lesson)

    return render(request, 'courses/edit_lesson.html', {
        'form': form,
        'lesson': lesson,
        'course': course
    })


# Delete a lesson
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course_id = lesson.course.id
    lesson.delete()
    messages.success(request, "Lesson deleted successfully!")
    return redirect('existing-lessons', course_id=course_id)



def all_courses(request):
    courses = Course.objects.all()
    return render(request, 'courses/all_courses.html', {'courses': courses})


def existing_lessons(request, course_id):
    # Get the course or return 404 if not found
    course = get_object_or_404(Course, id=course_id)
    
    # Get all lessons for this course
    lessons = Lesson.objects.filter(course=course).order_by('id')  # or any order you like
    
    context = {
        'course': course,
        'lessons': lessons,
        'year': datetime.now().year
    }
    
    return render(request, 'courses/existing_lessons.html', context)
