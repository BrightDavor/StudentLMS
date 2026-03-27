# chat/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import ChatMessage, Message, GroupChatMessage
from courses.models import Course
from .forms import MessageForm
from django.db.models import Q

User = get_user_model()

# -------------------------
# 1️⃣ Course Chat Views
# -------------------------
@login_required
def course_chat(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    messages_list = ChatMessage.objects.filter(course=course).order_by('timestamp')

    # ✅ Fix: use course.enrollments (not enrollment_set)
    if not course.enrollments.filter(student=request.user).exists() and course.lecturer != request.user:
        messages.error(request, "You are not allowed to view this course chat.")
        return redirect('home')

    if request.method == "POST":
        message_text = request.POST.get('message', '').strip()
        file = request.FILES.get('file')
        if message_text or file:
            ChatMessage.objects.create(user=request.user, course=course, message=message_text, file=file)
        return redirect('course-chat', course_id=course.id)

    return render(request, 'chat/course_chat.html', {'course': course, 'messages': messages_list})


@login_required
def edit_course_message(request, message_id):
    message = get_object_or_404(ChatMessage, id=message_id, user=request.user)
    if request.method == 'POST':
        message.message = request.POST.get('message', '').strip()
        message.timestamp = timezone.now()
        message.edited = True
        message.save()
        return redirect('course-chat', course_id=message.course.id)
    return render(request, 'chat/edit_course_message.html', {'message': message})


@login_required
def delete_course_message(request, message_id):
    message = get_object_or_404(ChatMessage, id=message_id, user=request.user)
    course_id = message.course.id
    message.delete()
    return redirect('course-chat', course_id=course_id)


# -------------------------
# 2️⃣ Private Chat (Student-Lecturer, Student-Student, Lecturer-Lecturer)
# -------------------------
@login_required
def private_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    # Fetch messages in both directions
    messages_list = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.receiver = other_user
            msg.save()
            return redirect('private-chat', user_id=other_user.id)
    else:
        form = MessageForm()

    return render(request, 'chat/private_chat.html', {
        'form': form,
        'messages': messages_list,
        'other_user': other_user
    })


@login_required
def edit_private_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    if request.method == 'POST':
        message.content = request.POST.get('message', '').strip()
        message.timestamp = timezone.now()
        message.save()
        return redirect('private-chat', user_id=message.receiver.id)
    return render(request, 'chat/edit_private_message.html', {'message': message})


@login_required
def delete_private_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    user_id = message.receiver.id
    message.delete()
    return redirect('private-chat', user_id=user_id)


# -------------------------
# 3️⃣ Group Chat Views
# -------------------------
@login_required
def student_group_chat(request, group_name):
    messages_list = GroupChatMessage.objects.filter(group_name=group_name).order_by('timestamp')
    return render(request, 'chat/student_group_chat.html', {'messages': messages_list, 'group_name': group_name})


@login_required
def send_group_message(request, group_name='Students'):
    if request.method == 'POST':
        content = request.POST.get('message', '').strip()
        if content:
            GroupChatMessage.objects.create(sender=request.user, content=content, group_name=group_name)
    return redirect('student-group-chat', group_name=group_name)


@login_required
def edit_group_message(request, message_id):
    message = get_object_or_404(GroupChatMessage, id=message_id, sender=request.user)
    if request.method == 'POST':
        message.content = request.POST.get('message', '').strip()
        message.timestamp = timezone.now()
        message.save()
        return redirect('student-group-chat', group_name=message.group_name)
    return render(request, 'chat/edit_group_message.html', {'message': message})


@login_required
def delete_group_message(request, message_id):
    message = get_object_or_404(GroupChatMessage, id=message_id, sender=request.user)
    group_name = message.group_name
    message.delete()
    return redirect('student-group-chat', group_name=group_name)


# -------------------------
# 4️⃣ Chat Lists (For UI)
# -------------------------
@login_required
def student_chat(request):
    """
    Students see lecturers of their courses and fellow students sharing courses
    """
    # ✅ Fixed plural related_name (enrollments)
    student_courses = Course.objects.filter(enrollments__student=request.user)

    # Lecturers teaching those courses
    lecturers = User.objects.filter(user_type='lecturer', courses__in=student_courses).distinct()

    # Fellow students sharing courses
    students = User.objects.filter(
        user_type='student',
        enrollments__course__in=student_courses
    ).exclude(id=request.user.id).distinct()

    return render(request, 'chat/student_chat.html', {
        'lecturers': lecturers,
        'students': students
    })


@login_required
def lecturer_chat(request):
    # ✅ Fixed plural related_name (enrollments)
    students = User.objects.filter(
        user_type='student',
        enrollments__course__lecturer=request.user
    ).distinct()

    lecturers = User.objects.filter(user_type='lecturer').exclude(id=request.user.id)

    return render(request, 'chat/lecturer_chat.html', {'lecturers': lecturers, 'students': students})


@login_required
def edit_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, sender=request.user)

    if request.method == "POST":
        content = request.POST.get("content")
        message.content = content
        message.save()
        return redirect('private-chat', user_id=message.receiver.id)

    return render(request, "chat/edit_message.html", {"message": message})


@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    receiver_id = message.receiver.id
    message.delete()
    return redirect('private-chat', user_id=receiver_id)
