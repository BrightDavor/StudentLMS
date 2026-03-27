from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),  # <-- namespace added
    path('courses/', include('courses.urls')),  # optional namespace for courses
    path('chat/', include('chat.urls')),  # optional namespace for chat
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
