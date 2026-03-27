from django.urls import path
from . import views

urlpatterns = [
    # Course chat
    path('course/<int:course_id>/', views.course_chat, name='course-chat'),
    path('course/edit/<int:message_id>/', views.edit_course_message, name='edit-course-message'),
    path('course/delete/<int:message_id>/', views.delete_course_message, name='delete-course-message'),

    # Private chats
    #path('private-chat/<int:user_id>/', views.lecturer_private_chat, name='private-chat'),
    path('edit-private/<int:message_id>/', views.edit_private_message, name='edit-private-message'),
    path('delete-private/<int:message_id>/', views.delete_private_message, name='delete-private-message'),

    # Lecturer to lecturer chat
    path('lecturer-chat/', views.lecturer_chat, name='lecturer-chat'),

    path('private-chat/<int:user_id>/', views.private_chat, name='private-chat'),
    path('lecturer-chat/', views.lecturer_chat, name='lecturer-chat'),
    path('student-chat/', views.student_chat, name='student-chat'),
    # Group chat

    path('private-chat/<int:receiver_id>/', views.private_chat, name='private-chat'),
    path('edit-message/<int:message_id>/', views.edit_message, name='edit-message'),
    path('delete-message/<int:message_id>/', views.delete_message, name='delete-message'),

    path('group/<str:group_name>/', views.student_group_chat, name='student-group-chat'),
    path('group/<str:group_name>/send/', views.send_group_message, name='send-group-message'),
    path('group/edit/<int:message_id>/', views.edit_group_message, name='edit-group-message'),
    path('group/delete/<int:message_id>/', views.delete_group_message, name='delete-group-message'),
]
