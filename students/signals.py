import os
import numpy as np
import cv2
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Student

@receiver(post_save, sender=Student)
def train_lbph_model(sender, instance, created, **kwargs):
    # Train the LBPH model whenever a student is saved
    try:
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        detector = cv2.CascadeClassifier(cascade_path)
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        faces = []
        ids = []
        
        students = Student.objects.all()
        for student in students:
            if student.image and student.image.name:
                image_path = student.image.path
                if os.path.exists(image_path):
                    img = cv2.imread(image_path)
                    if img is None:
                        continue
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    
                    # Detect faces
                    face_rects = detector.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
                    for (x, y, w, h) in face_rects:
                        faces.append(gray[y:y+h, x:x+w])
                        ids.append(student.id)
                        
        if len(faces) > 0:
            recognizer.train(faces, np.array(ids))
            
            # Save the model
            model_dir = os.path.join(settings.BASE_DIR, 'model')
            if not os.path.exists(model_dir):
                os.makedirs(model_dir)
            model_path = os.path.join(model_dir, 'trainer.yml')
            recognizer.write(model_path)
            print(f"LBPH model successfully trained on {len(faces)} faces and saved to {model_path}.")
        else:
            print("No valid faces found to train LBPH model.")
            
    except Exception as e:
        print(f"Error training LBPH model: {e}")
