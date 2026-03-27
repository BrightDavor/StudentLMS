from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'user_type', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type', 'profile_picture', 'country', 'region', 'bio')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
# Remove this line:
# admin.site.register(Course)  <-- DO NOT REGISTER COURSE HERE
