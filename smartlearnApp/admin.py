from django.contrib import admin
from .models import Classes


from .models import Classroom, Enrollment
@admin.register(Classes)
class ClassesAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'class_type', 'price', 'created_at')
    list_filter = ('class_type', 'owner')
    search_fields = ('title', 'description')

# ==========================================
# Phase 1 done here by Chan
# ==========================================


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'subject', 'class_type', 'price', 'created_at')
    list_filter = ('class_type', 'subject')
    search_fields = ('title', 'description')

# Register Enrollment
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'classroom', 'status', 'requested_at')
    list_filter = ('status', 'classroom')
    search_fields = ('student__username', 'classroom__title')

# ==========================================
# Phase 1 done here by yoon
# ==========================================
