from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('lecturer/register/', views.lecturer_register, name='lecturer-register'),
    path('lecturer/login/', views.lecturer_login, name='lecturer-login'),
    path('lecturer/logout/', views.lecturer_logout, name='lecturer-logout'),
    # Student
    path("register/", views.student_register, name="student-register"),

    path('lecturer-dashboard/', views.lecturer_dashboard, name='lecturer-dashboard'),
    path('lecturer-profile/', views.lecturer_profile, name='lecturer-profile'),
    path('lecturer-settings/', views.lecturer_settings, name='lecturer-settings'),  
    path('student-dashboard/', views.student_dashboard, name='student-dashboard'),
    path('student-courses/', views.student_courses, name='student-courses'),
    path('student-profile/', views.student_profile, name='student-profile'),
    path('student-results/', views.student_results, name='student-results'),
    path('student-certificates/', views.student_certificates, name='student-certificates'),
    path('student-notifications/', views.student_notifications, name='student-notifications'),

     path("student-settings/", views.student_settings, name="student-settings"),
path('subscribe-newsletter/', views.subscribe_newsletter, name='subscribe-newsletter'),
    # Chat

    # Static pages
    path('about-us/', views.about_us, name='about-us'),
    path('contact-us/', views.contact_us, name='contact-us'),
    path('privacy-policy/', views.privacy_policy, name='privacy-policy'),

    # Password reset (Django built-in)
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='accounts/password_reset_form.html'), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), 
         name='password_reset_complete'),
]
