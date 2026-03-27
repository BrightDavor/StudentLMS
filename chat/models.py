# chat/models.py
from django.db import models
from django.conf import settings
from accounts.models import CustomUser
from courses.models import Course

# -------------------------
# 1️⃣ Course Chat
# -------------------------
class ChatMessage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField(blank=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({self.course.title})"


# -------------------------
# 2️⃣ Student-to-Lecturer / Direct Chat
# -------------------------
class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)  # Optional: track if the message has been read

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username}: {self.content[:20]}"


# -------------------------
# 3️⃣ Group Chat
# -------------------------
class GroupChatMessage(models.Model):
    group_name = models.CharField(max_length=100)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='read_group_messages', blank=True)
    # read_by can track which users have read the message (optional)

    def __str__(self):
        return f"{self.sender.username} - {self.group_name}: {self.content[:20]}"
