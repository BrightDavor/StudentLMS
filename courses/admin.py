from django.contrib import admin
from .models import Department, Program, Course, Lesson, Enrollment, LessonMaterial

# ----------------------------
# Department & Program
# ----------------------------
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    list_filter = ('department',)
    search_fields = ('name',)


# ----------------------------
# Lesson & LessonMaterial
# ----------------------------
class LessonMaterialInline(admin.TabularInline):
    model = LessonMaterial
    extra = 1


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    inlines = [LessonMaterialInline]


# ----------------------------
# Course
# ----------------------------
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'program', 'lecturer', 'is_active', 'created_at')
    list_filter = ('lecturer', 'program', 'is_active')
    search_fields = ('title', 'lecturer__username', 'program__name')
    # Enables assigning a lecturer to a course directly in the admin


# ----------------------------
# Enrollment
# ----------------------------
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'lecturer', 'approved', 'date_enrolled')
    list_filter = ('approved', 'lecturer', 'course')
    search_fields = ('student__username', 'course__title', 'lecturer__username')
    readonly_fields = ('lecturer',)

    def save_model(self, request, obj, form, change):
        # Automatically assign lecturer if not already set
        if not obj.lecturer and obj.course and obj.course.lecturer:
            obj.lecturer = obj.course.lecturer
        super().save_model(request, obj, form, change)
