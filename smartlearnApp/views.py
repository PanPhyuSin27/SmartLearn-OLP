from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Classroom, Enrollment, Flashcard, MCQQuestion, QuizAttempt

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
    if request and request.user.is_authenticated:
        return request.user

    username = "TestUser"
    if request:
        # Check POST payload first (important for forms), then query string strings
        username = request.POST.get('user') or request.GET.get('user') or 'TestUser'

    user, created = User.objects.get_or_create(username=username)
    return user


def user_can_enter_classroom(classroom, user):
    if classroom.owner == user or classroom.class_type == 'public':
        return True

    return Enrollment.objects.filter(
        classroom=classroom,
        student=user,
        status='approved'
    ).exists()


def user_can_create_learning_content(classroom, user):
    if classroom.owner == user:
        return True

    return classroom.class_type == 'public'


def require_classroom_access(request, classroom):
    current_user = get_mock_user(request)
    if user_can_enter_classroom(classroom, current_user):
        return current_user, None

    messages.error(
        request,
        "You need approval from the class owner before entering this private classroom."
    )
    return current_user, redirect('browse_classes')


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
        class_type2 = request.POST.get('class_type', 'public')
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

    return redirect('manage_enrollments', class_id=enrollment.classroom.class_id)


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
def classroom_detail(request, class_id):

    classroom = get_object_or_404(
        Classroom,
        class_id=class_id
    )
    current_user, blocked_response = require_classroom_access(request, classroom)
    if blocked_response:
        return blocked_response

    return render(
        request,
        "classroom_detail.html",
        {
            "classroom": classroom
        }
    )

# ==========================================
# Phase 5 done here by MHK
# ==========================================


def flashcards_view(request, class_id):
    classroom = get_object_or_404(Classroom, class_id=class_id)
    current_user, blocked_response = require_classroom_access(request, classroom)
    if blocked_response:
        return blocked_response

    can_create = user_can_create_learning_content(classroom, current_user)

    if request.method == 'POST':
        if not can_create:
            messages.error(request, "Only the private class owner can create flashcards for this classroom.")
            return redirect('flashcards', class_id=classroom.class_id)

        topic = request.POST.get('topic', '').strip()
        front = request.POST.get('front', '').strip()
        back = request.POST.get('back', '').strip()

        if topic and front and back:
            Flashcard.objects.create(
                classroom=classroom,
                created_by=current_user,
                topic=topic,
                front=front,
                back=back
            )
            messages.success(request, "Flashcard shared with this classroom.")
            return redirect('flashcards', class_id=classroom.class_id)

        messages.error(request, "Please fill in topic, front, and back.")

    flashcards = Flashcard.objects.filter(classroom=classroom).select_related('created_by').order_by('topic', '-created_at')
    topics = Flashcard.objects.filter(classroom=classroom).order_by('topic').values_list('topic', flat=True).distinct()

    return render(request, 'flashcards.html', {
        'classroom': classroom,
        'flashcards': flashcards,
        'topics': topics,
        'can_create': can_create,
        'current_user': current_user,
    })


def mcqs_view(request, class_id):
    classroom = get_object_or_404(Classroom, class_id=class_id)
    current_user, blocked_response = require_classroom_access(request, classroom)
    if blocked_response:
        return blocked_response

    can_create = user_can_create_learning_content(classroom, current_user)

    if request.method == 'POST':
        if not can_create:
            messages.error(request, "Only the private class owner can create MCQs for this classroom.")
            return redirect('mcqs', class_id=classroom.class_id)

        topic = request.POST.get('topic', '').strip()
        question = request.POST.get('question', '').strip()
        option_a = request.POST.get('option_a', '').strip()
        option_b = request.POST.get('option_b', '').strip()
        option_c = request.POST.get('option_c', '').strip()
        option_d = request.POST.get('option_d', '').strip()
        correct_option = request.POST.get('correct_option', '').strip()
        explanation = request.POST.get('explanation', '').strip()

        if topic and question and option_a and option_b and option_c and option_d and correct_option:
            MCQQuestion.objects.create(
                classroom=classroom,
                created_by=current_user,
                topic=topic,
                question=question,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_option=correct_option,
                explanation=explanation
            )
            messages.success(request, "MCQ shared with this classroom.")
            return redirect('mcqs', class_id=classroom.class_id)

        messages.error(request, "Please complete the MCQ question and answer options.")

    questions = MCQQuestion.objects.filter(classroom=classroom).select_related('created_by').order_by('topic', '-created_at')
    topics = MCQQuestion.objects.filter(classroom=classroom).order_by('topic').values_list('topic', flat=True).distinct()

    return render(request, 'mcqs.html', {
        'classroom': classroom,
        'questions': questions,
        'topics': topics,
        'can_create': can_create,
        'current_user': current_user,
    })


def submit_quiz(request, class_id):
    classroom = get_object_or_404(Classroom, class_id=class_id)
    current_user, blocked_response = require_classroom_access(request, classroom)
    if blocked_response:
        return blocked_response

    if request.method != 'POST':
        return redirect('mcqs', class_id=classroom.class_id)

    questions = MCQQuestion.objects.filter(classroom=classroom).order_by('topic', 'question_id')
    answers = {}
    score = 0

    for question in questions:
        selected = request.POST.get(f'question_{question.question_id}', '')
        is_correct = selected == question.correct_option
        if is_correct:
            score += 1

        answers[str(question.question_id)] = {
            'selected': selected,
            'correct': question.correct_option,
            'is_correct': is_correct,
        }

    attempt = QuizAttempt.objects.create(
        classroom=classroom,
        student=current_user,
        score=score,
        total_questions=questions.count(),
        answers=answers
    )

    return redirect('quiz_result', attempt_id=attempt.attempt_id)


def quiz_result(request, attempt_id):
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related('classroom', 'student'),
        attempt_id=attempt_id
    )
    current_user, blocked_response = require_classroom_access(request, attempt.classroom)
    if blocked_response:
        return blocked_response

    if attempt.student != current_user and attempt.classroom.owner != current_user:
        messages.error(request, "You can only view your own quiz result.")
        return redirect('mcqs', class_id=attempt.classroom.class_id)

    questions = MCQQuestion.objects.filter(classroom=attempt.classroom).order_by('topic', 'question_id')
    reviewed_questions = []

    for question in questions:
        answer = attempt.answers.get(str(question.question_id), {})
        selected = answer.get('selected', '')
        reviewed_questions.append({
            'question': question,
            'selected': selected,
            'selected_text': question.option_text(selected),
            'correct_text': question.option_text(question.correct_option),
            'is_correct': answer.get('is_correct', False),
        })

    percentage = round((attempt.score / attempt.total_questions) * 100) if attempt.total_questions else 0

    return render(request, 'quiz_result.html', {
        'attempt': attempt,
        'classroom': attempt.classroom,
        'reviewed_questions': reviewed_questions,
        'percentage': percentage,
    })
