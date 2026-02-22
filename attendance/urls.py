from django.urls import path
from .views import (
    DashboardView,
    CameraCaptureView,
    AttendanceRecordsView,
    ExportAttendanceCSVView,
    FaceRecognitionAPIView
)

app_name = 'attendance'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('camera/', CameraCaptureView.as_view(), name='camera'),
    path('records/', AttendanceRecordsView.as_view(), name='records'),
    path('export/csv/', ExportAttendanceCSVView.as_view(), name='records_export'),
    
    # API endpoints
    path('api/recognize/', FaceRecognitionAPIView.as_view(), name='api_recognize_face'),
]
