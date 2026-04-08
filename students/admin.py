from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'reg_no', 'department', 'created_at')
    search_fields = ('name', 'reg_no')
    list_filter = ('department',)
