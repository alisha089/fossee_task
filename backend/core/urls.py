from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from api.views import UploadCSVView, HistoryView, GeneratePDFView, RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', RegisterView.as_view(), name='register'), # NEW
    path('api/upload/', UploadCSVView.as_view(), name='upload'),
    path('api/history/', HistoryView.as_view(), name='history'),
    path('api/pdf/<int:upload_id>/', GeneratePDFView.as_view(), name='generate_pdf'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
