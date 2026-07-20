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
    # Phase 2 done here by yoon
    # ==========================================


class Flashcard(models.Model):
    flashcard_id = models.AutoField(primary_key=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='flashcards')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flashcards')
    topic = models.CharField(max_length=120)
    front = models.TextField()
    back = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.topic} - {self.front[:40]}"


class MCQQuestion(models.Model):
    OPTION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]
    question_id = models.AutoField(primary_key=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='mcq_questions')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mcq_questions')
    topic = models.CharField(max_length=120)
    question = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES)
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.topic} - {self.question[:40]}"

    def option_text(self, option):
        return {
            'A': self.option_a,
            'B': self.option_b,
            'C': self.option_c,
            'D': self.option_d,
        }.get(option, '')


class QuizAttempt(models.Model):
    attempt_id = models.AutoField(primary_key=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='quiz_attempts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    answers = models.JSONField(default=dict)
    taken_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.classroom.title} ({self.score}/{self.total_questions})"
