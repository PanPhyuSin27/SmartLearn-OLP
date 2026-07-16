from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Classroom, Enrollment

def get_mock_user(request=None):
    username = "TestUser"
    if request:
        username = request.GET.get('user', request.POST.get('user', 'TestUser'))
    user, created = User.objects.get_or_create(username=username)
    return user

def home_view(request):
    return render(request, 'home.html')

def login_view(request):
    if request.user.is_authenticated: return redirect('dashboard')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('dashboard')
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        user = User.objects.create_user(username=request.POST.get('username'), password=request.POST.get('password1'))
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('dashboard')
    return render(request, 'register.html')


@login_required(login_url='login')
def dashboard_view(request):
    print(request.user.username)

    my_classes = Classroom.objects.filter(
        owner=request.user,
        created_from_site=True
    )

    return render(request, 'dashboard.html', {
        'my_classes': my_classes,
    })
@login_required(login_url='login')
def my_classes(request):
    classes = Classroom.objects.filter(owner=request.user)

    return render(request, 'my_classes.html', {
        'classes': classes
    })




def logout_view(request):
    logout(request)
    return redirect('home')


import django.contrib.messages as django_alerts

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Classroom, Enrollment


def get_mock_user(request=None):
    """ 
    ONE UNIFIED HELPER: Dynamically switch test users by checking POST body, 
    GET parameters, or falling back to 'TestUser'.
    """
    username = "TestUser"
    if request:
        # Check POST payload first (important for forms), then query string strings
        username = request.POST.get('user') or request.GET.get('user') or 'TestUser'

    user, created = User.objects.get_or_create(username=username)
    return user


def browse_classes(request):
    current_user = get_mock_user(request)

    # Start with all classrooms
    classrooms = Classroom.objects.all()

    # 1. Search Query Handling - Filtering matching your model's 'title' field
    search_query = request.GET.get('search', '')
    if search_query:
        classrooms = classrooms.filter(title__istartswith=search_query)

    # 2. Public / Private Visibility Filters - Matching model choices ('public'/'private')
    visibility = request.GET.get('visibility', '')
    if visibility == 'public':
        classrooms = classrooms.filter(class_type='public')
    elif visibility == 'private':
        classrooms = classrooms.filter(class_type='private')

    # 3. Alphabetical Sorting Filters - Sorting by 'title'
    sorting = request.GET.get('sorting', '')
    if sorting == 'az':
        classrooms = classrooms.order_by('title')
    elif sorting == 'za':
        classrooms = classrooms.order_by('-title')

    # Gather system relations for UI button matching
    user_enrollments = Enrollment.objects.filter(student=current_user)
    joined_class_ids = user_enrollments.filter(classroom_id__in=classrooms, status='approved').values_list(
        'classroom_id', flat=True)
    pending_class_ids = user_enrollments.filter(classroom_id__in=classrooms, status='pending').values_list(
        'classroom_id', flat=True)

    context = {
        'classrooms': classrooms,
        'search_query': search_query,
        'visibility': visibility,
        'sorting': sorting,
        'joined_class_ids': list(joined_class_ids),
        'pending_class_ids': list(pending_class_ids),
        'current_user_name': current_user.username,
    }
    return render(request, 'browserClass.html', context)



@login_required(login_url='login')
def create_class(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        class_type2 = request.POST.get('class_type')
        price = request.POST.get('price', 0.00)

        if class_type2 == 'public':
            price = 0.00

        Classroom.objects.create(
            title=title,
            subject=subject,
            description=description if description else "No description provided.",
            class_type=class_type2,
            price=price,
            owner=request.user ,  # ဒီနေရာကိုပြောင်း
            created_from_site=True
        )

        return redirect('dashboard')

    return render(request, 'createClass.html')



def delete_class(request, class_id):
    classroom = get_object_or_404(Classroom, class_id=class_id)
    current_user = get_mock_user(request)

    if classroom.owner == current_user:
        classroom.delete()
    return redirect(f"/classes/browse/?user={current_user.username}")







def request_join_class(request, class_id):
    current_user = get_mock_user(request)

    classroom = get_object_or_404(Classroom, class_id=class_id)

    # Prevent duplicate requests
    existing = Enrollment.objects.filter(
        student=current_user,
        classroom=classroom
    ).first()

    if not existing:
        Enrollment.objects.create(
            student=current_user,
            classroom=classroom,
            status='pending'
        )

    return redirect('browse_classes')





def manage_enrollments(request, class_id):
    classroom = get_object_or_404(Classroom, class_id=class_id)
    current_user = get_mock_user(request)

    if classroom.owner != current_user:
        return redirect(f"/classes/browse/?user={current_user.username}")

    pending_requests = Enrollment.objects.filter(classroom=classroom, status='pending')
    active_students = Enrollment.objects.filter(classroom=classroom, status='approved')

    context = {
        'classroom': classroom,
        'pending_requests': pending_requests,
        'active_students': active_students,
        'current_user_name': current_user.username,
    }
    return render(request, 'manage_enrollments.html', context)


def update_enrollment_status(request, enrollment_id, action):
    enrollment = get_object_or_404(Enrollment, enrollment_id=enrollment_id)
    current_user = get_mock_user(request)

    if enrollment.classroom.owner == current_user:
        if action == 'approve':
            enrollment.status = 'approved'
            enrollment.save()
        elif action == 'reject':
            enrollment.status = 'rejected'
            enrollment.save()

    return redirect('classes:manage_enrollments', class_id=enrollment.classroom.class_id)


def serve_dashboard_page(request):
    user = get_mock_user(request)
    return render(request, 'dashboard.html', {
        'current_user_name': user.username
    })


def profile_edit():
    return None

# ==========================================
# Phase 1 done here by yoon
# ==========================================
