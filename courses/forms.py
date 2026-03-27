from django import forms
from .models import Enrollment, Course, Lesson

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['course']

    def __init__(self, *args, program_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter courses by program if program_id is provided
        if program_id:
            self.fields['course'].queryset = Course.objects.filter(program_id=program_id)
        else:
            self.fields['course'].queryset = Course.objects.all()
        self.fields['course'].label = "Select Course"


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description']


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'video_url']
        # Removed 'file' because materials are handled separately

