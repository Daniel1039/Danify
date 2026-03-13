
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

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

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



# from django.urls import path
# from django.contrib.auth import views as auth_views
# from . import views
# from django.urls import path
# from .views import class_based_quiz_result

# urlpatterns = [
#     # Public pages
#     path('', views.home, name='home'),

#     # AUTH
#     path('signup/', views.signup, name='signup'),
#     path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
#     path('logout/', auth_views.LogoutView.as_view(), name='logout'),
#     # path("start-multiple-quiz/", views.start_multiple_quiz, name="start_multiple_quiz"),
#     # path('select-subjects/', views.select_subjects, name='select_subjects'),
#     # path('start-selected-quiz/', views.start_selected_quiz, name='start_selected_quiz'),
#     path('quiz/start/<int:quiz_id>/', views.take_quiz, name='start_quiz'),
#     path('pricing/', views.pricing, name='pricing'),
#     path('about/', views.about, name='about'),
#     # path('quiz/start-selected/', views.start_selected_quizzes, name='start_selected_quizzes'),  # needed!
    
    
#     path(
#     'quiz/start-selected/',
#     views.start_selected_quizzes,
#     name='start_selected_quizzes'
# ),
    

#     # PROTECTED PAGES (login required)
#     path('dashboard/', views.dashboard, name='dashboard'),
#     path('quiz/<int:quiz_id>/start/', views.start_quiz, name='start_quiz'),
#     path('quiz/take/', views.take_quiz, name='take_quiz'),
    
    
#     path(
#     "quiz/switch-subject/",
#     views.switch_subject,
#     name="switch_subject"
# ),


#     # Force submit when time is up
#     path('quiz/force-submit/', views.force_submit_quiz, name='force_submit_quiz'),
    
#     path("end-exam/<int:quiz_id>/", views.end_exam, name="end_exam"),
#     path('results/by-class/', views.class_results, name='class_results'),
#     path(
#     "class-results/",
#     class_based_quiz_result,
#     name="class_based_quiz_result"
# )


    

# ]
