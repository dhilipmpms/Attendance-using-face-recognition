import base64
import json
import numpy as np
import cv2
import face_recognition
from datetime import date, datetime
import csv

from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Attendance
from students.models import Student

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        
        total_students = Student.objects.count()
        # Count unique students present today
        present_today = Attendance.objects.filter(date=today, status='Present').values('student_id').distinct().count()
        absent_today = total_students - present_today
        attendance_percentage = (present_today / total_students * 100) if total_students > 0 else 0
        
        context['total_students'] = total_students
        context['present_today'] = present_today
        context['absent_today'] = absent_today
        context['attendance_percentage'] = round(attendance_percentage, 1)
        
        return context

class CameraCaptureView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/camera.html'

class AttendanceRecordsView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = 'attendance/records.html'
    context_object_name = 'records'
    ordering = ['-date', '-time']

class ExportAttendanceCSVView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="attendance_report_{date.today()}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Time', 'Registration No', 'Name', 'Department', 'Status'])
        
        attendances = Attendance.objects.all().order_by('-date', '-time')
        for att in attendances:
            writer.writerow([att.date, att.time, att.student.reg_no, att.student.name, att.student.department, att.status])
            
        return response

@method_decorator(csrf_exempt, name='dispatch')
class FaceRecognitionAPIView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            image_data = data.get('image')
            
            if not image_data:
                return JsonResponse({'success': False, 'message': 'No image provided'})
                
            # Decode base64 image
            format, imgstr = image_data.split(';base64,')
            img_bytes = base64.b64decode(imgstr)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert BGR (OpenCV) to RGB (face_recognition)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Find faces in current frame
            face_locations = face_recognition.face_locations(rgb_img)
            face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
            
            if not face_encodings:
                return JsonResponse({'success': False, 'message': 'No face detected'})
            
            # Load all students with encodings
            students = Student.objects.exclude(face_encoding__isnull=True).exclude(face_encoding__exact='')
            
            known_face_encodings = []
            known_face_ids = []
            
            for student in students:
                try:
                    encoding = np.array(json.loads(student.face_encoding))
                    known_face_encodings.append(encoding)
                    known_face_ids.append(student.id)
                except:
                    continue
            
            if not known_face_encodings:
                return JsonResponse({'success': False, 'message': 'No registered faces in database'})
            
            # Match faces
            match_found = False
            matched_student = None
            status_msg = ""
            
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                
                if matches and len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        student_id = known_face_ids[best_match_index]
                        matched_student = Student.objects.get(id=student_id)
                        match_found = True
                        
                        # Mark Attendance
                        today = date.today()
                        att, created = Attendance.objects.get_or_create(
                            student=matched_student,
                            date=today,
                            defaults={'status': 'Present'}
                        )
                        
                        status_msg = "Marked" if created else "Already Marked"
                        break
            
            if match_found:
                return JsonResponse({
                    'success': True,
                    'match_found': True,
                    'status': status_msg,
                    'time': datetime.now().strftime("%I:%M %p"),
                    'student': {
                        'name': matched_student.name,
                        'reg_no': matched_student.reg_no,
                        'department': matched_student.department,
                        'image_url': matched_student.image.url if matched_student.image else ''
                    }
                })
            else:
                return JsonResponse({'success': True, 'match_found': False, 'message': 'Face not recognized'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
