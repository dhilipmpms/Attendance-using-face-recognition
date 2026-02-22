from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'reg_no', 'department', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'reg_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Registration Number'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        }
