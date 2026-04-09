import base64
import json
import numpy as np
import cv2
import pandas as pd
import os
from django.conf import settings
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
            
            # Convert to grayscale for LBPH
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Load the trained LBPH model
            model_dir = os.path.join(settings.BASE_DIR, 'model')
            model_path = os.path.join(model_dir, 'trainer.yml')
            if not os.path.exists(model_path):
                return JsonResponse({'success': False, 'message': 'Recognition model not trained yet.'})
                
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.read(model_path)
            
            # Find face in current frame using Haar Cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            detector = cv2.CascadeClassifier(cascade_path)
            faces = detector.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
            
            if len(faces) == 0:
                return JsonResponse({'success': False, 'message': 'No face detected'})
                
            match_found = False
            matched_student = None
            status_msg = ""
            current_time = datetime.now().strftime("%I:%M %p")
            today = date.today()
            
            for (x, y, w, h) in faces:
                # Predict face
                id_, confidence = recognizer.predict(gray[y:y+h, x:x+w])
                
                # Confidence 0 is a perfect match (distance in LBPH), typically < 85 is considered a match
                if confidence < 85: 
                    try:
                        matched_student = Student.objects.get(id=id_)
                        match_found = True
                        
                        # Mark Attendance in DB
                        att, created = Attendance.objects.get_or_create(
                            student=matched_student,
                            date=today,
                            defaults={'status': 'Present'}
                        )
                        
                        status_msg = "Marked" if created else "Already Marked"
                        
                        # Also mark attendance using Pandas in CSV (as requested)
                        attendance_file = os.path.join(settings.BASE_DIR, 'Attendance.csv')
                        df = pd.DataFrame([
                            [today.strftime("%Y-%m-%d"), current_time, matched_student.reg_no, matched_student.name, matched_student.department, 'Present']
                        ], columns=['Date', 'Time', 'Registration No', 'Name', 'Department', 'Status'])
                        
                        # Append without headers if file exists, else create with headers
                        if not os.path.exists(attendance_file):
                            df.to_csv(attendance_file, index=False)
                        else:
                            df.to_csv(attendance_file, mode='a', header=False, index=False)
                            
                        break # Only process one verified face per frame
                    except Student.DoesNotExist:
                        continue
            
            if match_found:
                return JsonResponse({
                    'success': True,
                    'match_found': True,
                    'status': status_msg,
                    'time': current_time,
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
