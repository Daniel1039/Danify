from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    
    # Password Reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html'
         ), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    path("dashboard/", views.dashboard, name="dashboard"),
    path("start-exam/", views.start_exam, name="start_exam"),
    path("switch-subject/", views.switch_subject, name="switch_subject"),
    path("quiz/<int:quiz_id>/", views.take_quiz, name="take_quiz"),
    path("submit/", views.submit_exam, name="submit_exam"),
    path('quiz/<int:quiz_id>/bulk-upload/', views.bulk_question_upload, name='bulk_question_upload'),
    path('pricing/', views.pricing, name='pricing'),
    path('about/', views.about, name='about'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('register/', views.student_register, name='register'),
    path("contact/", views.contact, name="contact"),
    path('view-pdf/<path:path>/', views.view_pdf, name='view_pdf'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)