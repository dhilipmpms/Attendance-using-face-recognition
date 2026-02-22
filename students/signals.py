import os
import json
import numpy as np
import face_recognition
from PIL import Image
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Student

@receiver(post_save, sender=Student)
def generate_face_encoding(sender, instance, created, **kwargs):
    if instance.image:
        try:
            # We must only process if there is no encoding or we want to overwrite
            # Since face_recognition takes time, maybe only when created or image changed
            image_path = instance.image.path
            if os.path.exists(image_path):
                # Load image using face_recognition
                image = face_recognition.load_image_file(image_path)
                # Find face encodings
                face_encodings = face_recognition.face_encodings(image)
                
                if face_encodings:
                    # Take the first face found
                    encoding = face_encodings[0].tolist()
                    # We use post_save and disconnect/reconnect to prevent infinite recursion
                    post_save.disconnect(generate_face_encoding, sender=Student)
                    instance.face_encoding = json.dumps(encoding)
                    instance.save()
                    post_save.connect(generate_face_encoding, sender=Student)
        except Exception as e:
            print(f"Error generating face encoding: {e}")
