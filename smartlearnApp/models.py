from django.db import models
from django.contrib.auth.models import User

# ==========================================
# 1. CLASSES MODEL
# ==========================================
class Classes(models.Model):
    CLASS_TYPES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    class_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_classes')
    title = models.CharField(max_length=255)
    description = models.TextField()
    class_type = models.CharField(max_length=20, choices=CLASS_TYPES, default='public')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# ==========================================
# Phase 1 done here by Chan
# ==========================================


class Classroom(models.Model):
    SUBJECT_CHOICES = [
        ('math', 'Mathematics'),
        ('science', 'Science'),
        ('coding', 'Coding/IT'),
        ('languages', 'Languages'),
        ('arts', 'Arts & Design'),
    ]
    CLASS_TYPES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    class_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_classrooms', null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, default='math')
    class_type = models.CharField(max_length=20, choices=CLASS_TYPES, default='public', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    created_from_site = models.BooleanField(default=False)

    def __str__(self):
        return self.title if self.title else "Unnamed Classroom"



class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved / Active'),
        ('rejected', 'Rejected'),
    ]
    enrollment_id = models.AutoField(primary_key=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='enrollments', null=True, blank=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevents a student from requesting the same class more than once
        unique_together = ('classroom', 'student')

    def __str__(self):
        return f"{self.student.username} -> {self.classroom.title if self.classroom else 'No Classroom'} ({self.status})"


    # ==========================================
    # Phase 1 done here by yoon
    # ==========================================
