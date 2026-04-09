from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=150)
    reg_no = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)
    image = models.ImageField(upload_to='student_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.reg_no})"
