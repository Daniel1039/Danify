
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("start-exam/", views.start_exam, name="start_exam"),
    path("switch-subject/", views.switch_subject, name="switch_subject"),
    path("quiz/<int:quiz_id>/", views.take_quiz, name="take_quiz"),
    path("submit/", views.submit_exam, name="submit_exam"),
    path('quiz/<int:quiz_id>/bulk-upload/', views.bulk_question_upload, name='bulk_question_upload'),
    path('pricing/', views.pricing, name='pricing'),
    path('about/', views.about, name='about'),
    path('subscribe/', views.subscribe, name='subscribe'),  # ← THIS IS IMPORTANT
    path('register/', views.student_register, name='register'),
    path("contact/", views.contact, name="contact"),
    
    
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


