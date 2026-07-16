from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),              # Changed views.home to views.home_view
    path('login/', views.login_view, name='login'),      # Ensure this matches views.login_view
    path('register/', views.register_view, name='register'),  # Ensure this matches views.register_view
    path('dashboard/', views.dashboard_view, name='dashboard'), # Ensure this matches views.dashboard_view
    path('my-classes/', views.my_classes, name='my_classes'),
    path('logout/', views.logout_view, name='logout'),    # Ensure this matches views.logout_view
    path('home/', views.home_view, name='home'),  # Ensure this matches views.logout_view

    path('browse/', views.browse_classes, name='browse_classes'),
    path('create/', views.create_class, name='create_class'),
    path('delete/<int:class_id>/', views.delete_class, name='delete_class'),
    path('join-request/<int:class_id>/', views.request_join_class, name='request_join_class'),
    # path('dashboard.html', views.serve_dashboard_page, name='dashboard_page'),
     path('profile/edit/', views.profile_edit, name='profile_edit'),    # Teacher features
    path('manage/<int:class_id>/', views.manage_enrollments, name='manage_enrollments'),
    path('enrollment-decision/<int:enrollment_id>/<str:action>/', views.update_enrollment_status, name='update_enrollment_status'),
]



# ==========================================
# Phase 1 done here by Chan,yoon
# ==========================================
