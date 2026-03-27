from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from .forms import StudentRegistrationForm, LecturerRegistrationForm, LecturerLoginForm
from .models import CustomUser
from courses.models import Course, Enrollment, Notification, Certificate


# -------------------------
# Helper
# -------------------------
def admin_only(user):
    return user.user_type == 'admin'

# User Login (for both roles)
# -------------------------------
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()   # use email
        password = request.POST.get('password', '').strip()

        if not email or not password:
            messages.error(request, "Please enter both email and password.")
            return render(request, 'accounts/student_login.html')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                if user.user_type == 'lecturer':
                    return redirect('lecturer-dashboard')
                else:
                    return redirect('student-dashboard')
            else:
                messages.error(request, "Your account is inactive. Contact admin.")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'accounts/student_login.html')

# -------------------------
# Student Registration
# -------------------------
def student_register(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'student'
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('student_login')
    else:
        form = StudentRegistrationForm()
    return render(request, 'accounts/student_register.html', {'form': form})


# -------------------------
# Lecturer Registration (Admin only)
# -------------------------
@login_required
@user_passes_test(admin_only)
def register_lecturer(request):
    if request.method == 'POST':
        form = LecturerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'lecturer'
            user.save()
            messages.success(request, "Lecturer registered successfully.")
            return redirect('admin-dashboard')
    else:
        form = LecturerRegistrationForm()
    return render(request, 'accounts/register_lecturer.html', {'form': form})


# -------------------------
# Lecturer Self Registration
# -------------------------
def lecturer_register(request):
    if request.method == 'POST':
        form = LecturerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'lecturer'
            user.save()
            messages.success(request, 'Lecturer account created successfully. You can now log in.')
            return redirect('lecturer-login')
    else:
        form = LecturerRegistrationForm()
    return render(request, 'accounts/lecturer_register.html', {'form': form})


# -------------------------
# Lecturer Login
# -------------------------
def lecturer_login(request):
    if request.method == 'POST':
        form = LecturerLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.user_type == 'lecturer':
                login(request, user)
                return redirect('lecturer-dashboard')
            else:
                messages.error(request, 'You are not authorized as a lecturer.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LecturerLoginForm()
    return render(request, 'accounts/lecturer_login.html', {'form': form})


# -------------------------
# Logout
# -------------------------
def user_logout(request):
    logout(request)
    return redirect('home')


# -------------------------
# Dashboards
# -------------------------
@login_required
def student_dashboard(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    return render(request, 'accounts/student_dashboard.html', {'enrollments': enrollments})



# -------------------------
# Student Profile, Results, Certificates
# -------------------------
@login_required
def student_profile(request):
    if request.user.user_type != 'student':
        return redirect('home')
    return render(request, 'accounts/student_profile.html', {'student': request.user})


@login_required
def student_results(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    return render(request, 'accounts/student_results.html', {
        'enrollments': enrollments,
        'student': request.user
    })


@login_required
def student_certificates(request):
    certificates = Certificate.objects.filter(enrollment__student=request.user)
    return render(request, 'accounts/student_certificates.html', {
        'student': request.user,
        'certificates': certificates
    })


# -------------------------
# Miscellaneous
# -------------------------
def home(request):
    courses = Course.objects.all()  # Fetch all courses
    year = datetime.now().year
    return render(request, 'accounts/home.html', {'courses': courses, 'year': year})

def about_us(request):
    return render(request, 'accounts/about_us.html')

def contact_us(request):
    return render(request, 'accounts/contact_us.html')

def privacy_policy(request):
    return render(request, 'accounts/privacy_policy.html')

@csrf_exempt
def subscribe_newsletter(request):
    if request.method == "POST":
        email = request.POST.get("email")
        print(f"New subscriber: {email}")
        return HttpResponse("Thank you for subscribing!")
    return HttpResponse("Invalid request.")

def user_logout(request):
    logout(request)
    return redirect('login')

def lecturer_logout(request):
    logout(request)
    return redirect('lecturer-login')

# -------------------------
# Student Courses
# -------------------------

@login_required
def student_courses(request):
    from courses.models import Enrollment  # import locally to avoid circular import
    enrollments = Enrollment.objects.filter(student=request.user)
    context = {
        'enrollments': enrollments,
        'student': request.user
    }
    return render(request, 'accounts/student_courses.html', context)

@login_required
def student_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/student_notifications.html', {'notifications': notifications})

@login_required
def lecturer_dashboard(request):
    user = request.user
    # Get courses taught by the lecturer
    courses = Course.objects.filter(lecturer=user)
    return render(request, 'accounts/lecturer_dashboard.html', {
        'courses': courses,
        'year': 2025  # or use datetime.now().year dynamically
    })

@login_required
def lecturer_profile(request):
    """
    Display lecturer profile with info and profile picture.
    """
    user = request.user
    return render(request, 'accounts/lecturer_profile.html', {  # <-- Use 'accounts/lecturer_profile.html'
        'lecturer': user
    })

@login_required
def lecturer_settings(request):
    if request.method == "POST":
        theme = request.POST.get("theme")
        language = request.POST.get("language")

        user = request.user
        if theme:
            user.theme = theme
        if language:
            user.language = language
        user.save()

        # If AJAX request, return JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return redirect('lecturer-dashboard')

    return render(request, 'accounts/lecturer_settings.html')


@login_required
def lecturer_profile(request):
    user = request.user

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        bio = request.POST.get("bio")
        nationality = request.POST.get("nationality")
        date_of_birth = request.POST.get("date_of_birth")
        gender = request.POST.get("gender")
        profile_picture = request.FILES.get("profile_picture")

        if full_name:
            user.first_name = full_name.split(" ")[0]
            user.last_name = " ".join(full_name.split(" ")[1:]) if len(full_name.split(" ")) > 1 else ""
        if bio is not None:
            user.bio = bio
        if nationality is not None:
            user.nationality = nationality
        if date_of_birth:
            user.date_of_birth = date_of_birth
        if gender is not None:
            user.gender = gender
        if profile_picture:
            user.profile_picture = profile_picture

        user.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            profile_url = user.profile_picture.url if user.profile_picture else None
            return JsonResponse({'success': True, 'profile_picture_url': profile_url})

        return redirect('lecturer-dashboard')

    return render(request, 'accounts/lecturer_profile.html', {'user': user})

@login_required
def lecturer_settings(request):
    user = request.user

    if request.method == 'POST':

        user.full_name = request.POST.get('full_name', '')
        user.bio = request.POST.get('bio', '')
        user.nationality = request.POST.get('nationality', '')
        user.gender = request.POST.get('gender', '')
        user.theme = request.POST.get('theme', 'light')
        user.language = request.POST.get('language', 'English')

        # ✅ SAFE date handling
        dob = request.POST.get('date_of_birth')
        if dob:
            parsed_date = parse_date(dob)
            if parsed_date:
                user.date_of_birth = parsed_date

        # ✅ Profile picture (safe)
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']

        user.save()

        # ✅ AJAX response
        return JsonResponse({
            "success": True,
            "redirect_url": "/lecturer-dashboard/"
        })

    return render(request, 'accounts/lecturer_settings.html', {'user': user})

@login_required
def student_settings(request):
    if request.method == "POST":
        user = request.user

        theme = request.POST.get("theme")
        language = request.POST.get("language")
        date_of_birth = request.POST.get("date_of_birth")

        if theme:
            user.theme = theme
        if language:
            user.language = language
        if date_of_birth:
            user.date_of_birth = date_of_birth  # must be YYYY-MM-DD

        user.save()

        # AJAX response
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True})

        return redirect("student-dashboard")

    return render(request, "accounts/student_settings.html")