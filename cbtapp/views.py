from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Quiz, Question

from .models import SchoolClass, ClassArm, StudentProfile
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Attempt, StudentProfile
from django.conf import settings
from .models import ContactMessage


from django.shortcuts import render
from .models import StudentProfile, Quiz
def home(request):
    try:
        profile = StudentProfile.objects.get(user=request.user)

        quizzes = Quiz.objects.filter(
            school_class=profile.school_class,
            arms=profile.arm
        )

    except StudentProfile.DoesNotExist:
        quizzes = Quiz.objects.none()

    return render(request, 'home.html', {'quizzes': quizzes})
def pricing(request):
    return render(request, 'pricing.html')

def about(request):
    return render(request, 'about.html')

from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings

def contact(request):

    if request.method == "POST":
        first_name = request.POST.get("firstName")
        last_name = request.POST.get("lastName")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        full_message = f"""
"""       # SAVE TO DATABASE
        ContactMessage.objects.create(
            name=f"{first_name} {last_name}",
            email=email,
            subject=subject,
            message=message
        )

       
       
       
       
       
       

        return render(request, "contact.html", {"success": True})

    return render(request, "contact.html")



from django.views.decorators.csrf import ensure_csrf_cookie
@ensure_csrf_cookie
def login_view(request):
    classes = SchoolClass.objects.all()
    arms = ClassArm.objects.all()
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        class_id = request.POST.get("school_class")
        arm_id = request.POST.get("arm")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                profile = StudentProfile.objects.get(user=user)
                if (
                    str(profile.school_class.id) == class_id and
                    str(profile.arm.id) == arm_id
                ):
                    login(request, user)
                    return redirect("dashboard")
                else:
                    error = "Selected class or arm is incorrect"
            except StudentProfile.DoesNotExist:
                error = "Student profile not found"
        else:
            error = "Invalid username or password"
    return render(request, "registration/login.html", {
        "classes": classes,
        "arms": arms,
        "error": error
    })







# ===============================
# DASHBOARD
# ===============================

from .models import Attempt
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Subscription
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Subscription
from django.utils import timezone
from django.utils import timezone
from django.shortcuts import render, redirect
from .models import Subscription, StudentProfile, Quiz, Attempt


@login_required

def dashboard(request):
    # Check subscription
    try:
        subscription = Subscription.objects.get(user=request.user)
        if not subscription.is_active():
            return redirect("subscribe")
    except Subscription.DoesNotExist:
        return redirect("subscribe")

    # ✅ Get student profile and quizzes
    try:
        profile = StudentProfile.objects.get(user=request.user)

        # Fix: use 'arms__in' for ManyToManyField
        quizzes = Quiz.objects.filter(
            school_class=profile.school_class,
            arms__in=[profile.arm]  # profile.arm is the student's arm
        ).distinct()

    except StudentProfile.DoesNotExist:
        quizzes = Quiz.objects.none()

    # Get user's attempts
    attempts = Attempt.objects.filter(user=request.user).order_by('-taken_at')

    # Calculate remaining subscription time
    delta = subscription.end_date - timezone.now()
    days_left = max(delta.days, 0)
    time_remaining = delta.total_seconds()

    return render(request, "dashboard.html", {
        "quizzes": quizzes,
        "attempts": attempts,
        "subscription": subscription,
        "days_left": days_left,
        "time_remaining": time_remaining
    })
# def dashboard(request):
    # quizzes = Quiz.objects.all()
    # return render(request, "dashboard.html", {"quizzes": quizzes})
# 

# ===============================
# START EXAM (MULTI SUBJECT)
# ===============================
# ===============================
# START EXAM (PROFESSIONAL MODE - GLOBAL TIMER)
# ===============================
@login_required
def start_exam(request):
    if request.method == "POST":
        selected = request.POST.getlist("subjects")

        if not selected:
            return redirect("dashboard")

        quizzes = Quiz.objects.filter(id__in=selected)

        # Store selected quizzes
        request.session["selected_quizzes"] = [str(q.id) for q in quizzes]
        request.session["current_quiz_index"] = 0
        request.session["answers"] = {}
        request.session["question_indexes"] = {}

        # ✅ GLOBAL TIMER (sum of all subjects)
        total_exam_seconds = sum(q.time_limit for q in quizzes) * 60
        request.session["total_exam_seconds"] = total_exam_seconds
        request.session["start_time"] = timezone.now().isoformat()

        return redirect("take_quiz", quiz_id=quizzes.first().id)

    return redirect("dashboard")


# ===============================
# SWITCH SUBJECT
# ===============================
def switch_subject(request):
    if request.method == "POST":
        quiz_id = request.POST.get("quiz_id")
        return redirect("take_quiz", quiz_id=quiz_id)


# ===============================
# TAKE QUIZ
# ==============================
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # =========================
    # SAFE ATTEMPT CREATION
    # =========================
    if request.user.is_authenticated:
        attempt_key = f"attempt_{quiz_id}"
        attempt_id = request.session.get(attempt_key)

        if not attempt_id:
            try:
                profile = StudentProfile.objects.get(user=request.user)

                attempt = Attempt.objects.create(
                    user=request.user,
                    quiz=quiz,
                    school_class=profile.school_class,
                    arm=profile.arm,
                )

                request.session[attempt_key] = attempt.id
            except StudentProfile.DoesNotExist:
                pass

    questions = Question.objects.filter(quiz=quiz)

    if not questions.exists():
        return render(request, "no_questions.html")

    question_indexes = request.session.get("question_indexes", {})
    index = question_indexes.get(str(quiz_id), 0)
    answers = request.session.get("answers", {})

    # =========================
    # HANDLE POST
    # =========================
    if request.method == "POST":
        selected_answer = request.POST.get("answer")
        question_id = str(questions[index].id)

        if selected_answer:
            answers[question_id] = selected_answer
            request.session["answers"] = answers

        if "next" in request.POST:
            index += 1
        elif "prev" in request.POST:
            index -= 1
        elif "jump" in request.POST:
            index = int(request.POST.get("jump"))
        elif "submit" in request.POST or "end_exam" in request.POST:
            return redirect("submit_exam")

        question_indexes[str(quiz_id)] = index
        request.session["question_indexes"] = question_indexes

        return redirect("take_quiz", quiz_id=quiz.id)

    # =========================
    # TIMER
    # =========================
        # =========================
    # GLOBAL EXAM TIMER (JAMB STYLE)
    # =========================
    remaining_seconds = None

    start_time_str = request.session.get("start_time")
    total_exam_seconds = request.session.get("total_exam_seconds")

    if start_time_str and total_exam_seconds:
        start_time = timezone.datetime.fromisoformat(start_time_str)
        elapsed = (timezone.now() - start_time).total_seconds()
        remaining_seconds = max(0, int(total_exam_seconds - elapsed))

        # 🔥 AUTO SUBMIT WHEN TIME FINISHES
        if remaining_seconds <= 0:
            return redirect("submit_exam")

    selected_quizzes = request.session.get("selected_quizzes", [])
    quiz_map = {
        str(q.id): q.title for q in Quiz.objects.filter(id__in=selected_quizzes)
    }

    context = {
        "quiz": quiz,
        "questions": questions,
        "question": questions[index],
        "index": index,
        "total_questions": questions.count(),
        "answers": answers,
        "selected": answers.get(str(questions[index].id)),
        "remaining_seconds": remaining_seconds,
        "quiz_map": quiz_map,
    }

    return render(request, "take_quiz.html", context)



@login_required
def subscribe(request):

    subscription, created = Subscription.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        receipt = request.FILES.get("receipt")

        if receipt:
            subscription.receipt = receipt
            subscription.status = "pending"
            subscription.save()

            return render(request, "pending.html")

    return render(request, "subscribe.html")


# ===============================
 # SUBMIT EXAM
# ===============================
from django.shortcuts import render
from .models import Quiz, Question, Attempt
@login_required
def submit_exam(request):
    answers = request.session.get("answers", {})

    total_score = 0
    total_marks = 0

    subject_results = {}

    for key, value in request.session.items():
        if key.startswith("attempt_"):
            quiz_id = key.split("_")[1]

            try:
                quiz = Quiz.objects.get(id=quiz_id)
                attempt = Attempt.objects.get(id=value)
            except (Quiz.DoesNotExist, Attempt.DoesNotExist):
                continue

            questions = Question.objects.filter(quiz=quiz)

            quiz_score = 0
            quiz_total = 0

            # Get subject name
            subject_name = quiz.subject.name if quiz.subject else "General"

            # Create subject entry if not exists
            if subject_name not in subject_results:
                subject_results[subject_name] = {
                    "subject": subject_name,
                    "score": 0,
                    "total": 0,
                    "wrong_questions": []
                }

            for question in questions:
                quiz_total += question.marks
                selected_answer = answers.get(str(question.id))

                options = {
                    "A": question.option_a,
                    "B": question.option_b,
                    "C": question.option_c,
                    "D": question.option_d,
                }

                if selected_answer == question.correct_option:
                    quiz_score += question.marks
                else:
                    subject_results[subject_name]["wrong_questions"].append({
                        "question_text": question.text,
                        "options": options,
                        "selected": selected_answer,
                        "correct": question.correct_option,
                        "explanation": question.explanation,
                    })

            attempt.score = quiz_score
            attempt.total_marks = quiz_total
            attempt.save()

            # Add subject score
            subject_results[subject_name]["score"] += quiz_score
            subject_results[subject_name]["total"] += quiz_total

            total_score += quiz_score
            total_marks += quiz_total

    percentage = (total_score / total_marks * 100) if total_marks else 0

    # Clean session
    for key in list(request.session.keys()):
        if key.startswith("attempt_") or key in [
            "answers",
            "selected_quizzes",
            "question_indexes",
            "start_time",
            "total_exam_seconds",
        ]:
            del request.session[key]

    return render(request, "result.html", {
        "score": total_score,
        "total": total_marks,
        "percentage": round(percentage, 2),
        "subject_results": subject_results.values(),  # IMPORTANT
    })



# views.py
# import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Quiz, Question, Subject

from .forms import BulkQuestionUploadForm

def bulk_question_upload(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)

    if request.method == "POST":
        form = BulkQuestionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']

            try:
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.name.endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(file)
                else:
                    messages.error(request, "File format not supported.")
                    return redirect(request.path)

                # Iterate through rows
                for index, row in df.iterrows():
                    Question.objects.create(
                        quiz=quiz,
                        subject=quiz.subject,
                        text=row['text'],
                        option_a=row['option_a'],
                        option_b=row['option_b'],
                        option_c=row['option_c'],
                        option_d=row['option_d'],
                        correct_option=row['correct_option'],
                        marks=row.get('marks', 1)
                    )

                messages.success(request, "Questions uploaded successfully!")
                return redirect('quiz_detail', quiz_id=quiz.id)

            except Exception as e:
                messages.error(request, f"Error processing file: {e}")
                return redirect(request.path)
    else:
        form = BulkQuestionUploadForm()

    return render(request, 'bulk_upload.html', {'form': form, 'quiz': quiz})


# views.py
def start_selected_quizzes(request):
    if request.method == "POST":
        selected_quiz_ids = request.POST.getlist('selected_quizzes')
        quizzes = Quiz.objects.filter(id__in=selected_quiz_ids)

        # Store selected quizzes
        request.session['selected_quizzes'] = [str(q.id) for q in quizzes]

        # Store total time = sum of selected subjects
        total_time = sum(q.time_limit for q in quizzes)
        request.session['total_quiz_time'] = total_time  # in minutes

        # Optionally store individual times if needed
        quiz_times = {str(q.id): q.time_limit for q in quizzes}
        request.session['quiz_times'] = quiz_times

        # Set first quiz as current
        request.session['current_quiz'] = str(quizzes[0].id)

        return redirect('take_quiz', quiz_id=quizzes[0].id)





from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import StudentRegisterForm, StudentProfileForm


def student_register(request):

    if request.method == "POST":
        user_form = StudentRegisterForm(request.POST)
        profile_form = StudentProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():

            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            messages.success(request, "Account created successfully. You can now login.")
            return redirect('login')

    else:
        user_form = StudentRegisterForm()
        profile_form = StudentProfileForm()

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'register.html', context)






# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth import login, logout
# from django.views.decorators.csrf import csrf_exempt
# from django.http import HttpResponse, JsonResponse
# from .models import Quiz, Question, Attempt
# from .forms import SignUpForm
# import random, time
# from django.contrib.auth import authenticate
# from .models import SchoolClass, ClassArm, StudentProfile
# import csv

# from django.shortcuts import redirect, get_object_or_404




# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login
# from .models import SchoolClass, ClassArm, StudentProfile



# from django.contrib.auth import authenticate, login
# from django.shortcuts import render, redirect

# from django.contrib.auth import authenticate, login
# from django.shortcuts import render, redirect
# from .models import StudentProfile

# from django.views.decorators.csrf import ensure_csrf_cookie
# @ensure_csrf_cookie
# def login_view(request):
#     classes = SchoolClass.objects.all()
#     arms = ClassArm.objects.all()
#     error = None

#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         class_id = request.POST.get("school_class")
#         arm_id = request.POST.get("arm")

#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             try:
#                 profile = StudentProfile.objects.get(user=user)

#                 if (
#                     str(profile.school_class.id) == class_id and
#                     str(profile.arm.id) == arm_id
#                 ):
#                     login(request, user)
#                     return redirect("dashboard")
#                 else:
#                     error = "Selected class or arm is incorrect"

#             except StudentProfile.DoesNotExist:
#                 error = "Student profile not found"

#         else:
#             error = "Invalid username or password"

#     return render(request, "registration/login.html", {
#         "classes": classes,
#         "arms": arms,
#         "error": error
#     })



# @login_required
# def home(request):
#     try:
#         profile = StudentProfile.objects.get(user=request.user)
#         quizzes = Quiz.objects.filter(
#             school_class=profile.school_class,
#             arm=profile.arm
#         )
#     except StudentProfile.DoesNotExist:
#         quizzes = Quiz.objects.none()

#     return render(request, 'home.html', {'quizzes': quizzes})




# def pricing(request):
#     return render(request, 'pricing.html')



# def about(request):
#     return render(request, 'about.html')

# def signup(request):
#     if request.method == 'POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('dashboard')
#     else:
#         form = SignUpForm()
#     return render(request, 'registration/signup.html', {'form': form})


# @login_required

# def start_quiz(request, quiz_id):
#      # MULTI-SUBJECT SUPPORT (SAFE)
#     selected = request.session.get("selected_quizzes")
#     index = request.session.get("current_quiz_index", 0)

#     if selected:
#         quiz_id = int(selected[index])
#     quiz = get_object_or_404(Quiz, id=quiz_id)

#     # Get all questions for this quiz
#     qs = list(quiz.questions.all())

#     # 🔹 Shuffle questions for randomness per attempt/user
#     random.shuffle(qs)

#     # 🔹 Limit to quiz.total_questions safely
#     selected = qs[:min(len(qs), quiz.total_questions)]

#     # 🔹 Store everything in session (DO NOT CHANGE KEYS)
#     request.session['current_quiz'] = quiz.id
#     request.session['question_ids'] = [q.id for q in selected]
#     request.session['current_index'] = 0
#     request.session['answers'] = {}
#     request.session['quiz_start_time'] = time.time()

#     return redirect('take_quiz')

# @login_required
# def take_quiz(request):
#     qids = request.session.get('question_ids')
#     quiz_id = request.session.get('current_quiz')

#     if not qids or not quiz_id:
#         return HttpResponse('No quiz in progress.')

#     quiz = get_object_or_404(Quiz, id=quiz_id)
#     questions = [Question.objects.get(id=qid) for qid in qids]

#     index = request.session.get('current_index', 0)
#     answers = request.session.get('answers', {})

#     # ✅ answered question IDs (for navigation colors)
#     answered_ids = answers.keys()

#     index = max(0, min(index, len(questions) - 1))
#     question = questions[index]
#     question_range = range(len(questions))

#     if request.method == 'POST':

#         # ⏰ AUTO SUBMIT (TIME UP) 
#         if 'auto_submit' in request.POST:
#             return finalize_quiz(request)

#         # 🔴 END EXAM BUTTON
#         if 'end_exam' in request.POST:
#             return finalize_quiz(request)

#         # ✅ Save answer
#         selected = request.POST.get('answer')
#         if selected:
#             answers[str(question.id)] = selected
#             request.session['answers'] = answers

#         if 'next' in request.POST:
#             request.session['current_index'] = index + 1
#             return redirect('take_quiz')

#         if 'prev' in request.POST:
#             request.session['current_index'] = index - 1
#             return redirect('take_quiz')

#         if 'jump' in request.POST:
#             request.session['current_index'] = int(request.POST.get('jump'))
#             return redirect('take_quiz')

#         if 'submit' in request.POST:
#             return finalize_quiz(request)

#     # ⏱ TIMER
#     remaining_seconds = None
#     start = request.session.get('quiz_start_time')
#     if start:
#         elapsed = int(time.time() - start)
#         remaining_seconds = max(0, quiz.time_limit * 60 - elapsed)
        
        
#     return render(request, 'take_quiz.html', {
#     'question': question,
#     'quiz': quiz,
#     'index': index,
#     'total_questions': len(questions),
#     'question_range': question_range,
#     'questions': questions,      # ✅ ADD THIS
#     'answers': answers,          # ✅ ADD THIS
#     'selected': answers.get(str(question.id)),
#     'remaining_seconds': remaining_seconds
# })


# @login_required
# def start_selected_quizzes(request):
#     if request.method != "POST":
#         return redirect("dashboard")

#     quiz_ids = request.POST.getlist("selected_quizzes")

#     if not quiz_ids:
#         return redirect("dashboard")

#     # ✅ Save selected quizzes in session
#     request.session["selected_quizzes"] = quiz_ids
#     request.session["current_quiz_index"] = 0

#     # ▶ Start first quiz
#     return redirect("start_quiz", quiz_id=int(quiz_ids[0]))




# # from django.shortcuts import redirect
# import time
# def finalize_quiz(request):
#     qids = request.session.get('question_ids')
#     quiz_id = request.session.get('current_quiz')
#     answers = request.session.get('answers', {})

#     quiz = Quiz.objects.get(id=quiz_id)
#     questions = [Question.objects.get(id=qid) for qid in qids]

#     start = request.session.get('quiz_start_time') or time.time()
#     duration = int(time.time() - start)

#     score = 0
#     total = sum(q.marks for q in questions)

#     for q in questions:
#         if answers.get(str(q.id)) == q.correct_option:
#             score += q.marks

#     Attempt.objects.create(
#         user=request.user,
#         quiz=quiz,
#         school_class=quiz.school_class,
#         arm=quiz.arm,
#         score=score,
#         total_marks=total
#     )

#     # 🧹 clear per-quiz session
#     for k in (
#         'current_quiz',
#         'question_ids',
#         'quiz_start_time',
#         'current_index',
#         'answers'
#     ):
#         request.session.pop(k, None)

#     # ===============================
#     # ✅ MULTI-SUBJECT CONTINUATION
#     # ===============================
#     selected = request.session.get("selected_quizzes")
#     index = request.session.get("current_quiz_index", 0)

#     if selected:
#         index += 1
#         if index < len(selected):
#             request.session["current_quiz_index"] = index
#             return redirect("start_quiz", quiz_id=int(selected[index]))

#         # all done
#         request.session.pop("selected_quizzes", None)
#         request.session.pop("current_quiz_index", None)

#     return redirect("login")


# @login_required
# def switch_subject(request):
#     if request.method != "POST":
#         return redirect("take_quiz")

#     quiz_id = request.POST.get("quiz_id")
#     if not quiz_id:
#         return redirect("take_quiz")

#     # 🔹 Clear only CURRENT quiz state
#     for k in (
#         "current_quiz",
#         "question_ids",
#         "current_index",
#         "answers",
#         "quiz_start_time",
#     ):
#         request.session.pop(k, None)

#     # 🔹 Start chosen subject
#     return redirect("start_quiz", quiz_id=int(quiz_id))










# # 
# # def finalize_quiz(request):
#     # qids = request.session.get('question_ids')
#     # quiz_id = request.session.get('current_quiz')
#     # answers = request.session.get('answers', {})
# # 
#     # quiz = Quiz.objects.get(id=quiz_id)
#     # questions = [Question.objects.get(id=qid) for qid in qids]
# # 
#     # start = request.session.get('quiz_start_time') or time.time()
#     # duration = int(time.time() - start)
# # 
#     # score = 0
#     # total = sum(q.marks for q in questions)
# # 
#     # for q in questions:
#         # if answers.get(str(q.id)) == q.correct_option:
#             # score += q.marks
# # 
#     # Attempt.objects.create(
#         # user=request.user,
#         # quiz=quiz,
#         # school_class=quiz.school_class,
#         # arm=quiz.arm,
#         # score=score,
#         # total_marks=total
#     # )
# # 
#     # clear session safely
#     # for k in (
#         # 'current_quiz',
#         # 'question_ids',
#         # 'quiz_start_time',
#         # 'current_index',
#         # 'answers'
#     # ):
#         # request.session.pop(k, None)
# # 
#     # ✅ REAL redirect (URL changes)
#     # return redirect('login')

    
    
    
    
# from django.urls import reverse

#     # 
# # @csrf_exempt
# # @login_required
# from django.http import JsonResponse
# from django.urls import reverse
# from django.contrib.auth import logout
# from django.views.decorators.http import require_POST

# @require_POST
# def force_submit_quiz(request):
#     # finalize quiz safely
#     finalize_quiz(request)

#     # logout user AFTER submission
#     logout(request)

#     # tell JS exactly where to go
#     return JsonResponse({
#         "status": "ok",
#         "redirect": reverse("login")
#     })


# @login_required
# def dashboard(request):
#     attempts = Attempt.objects.filter(user=request.user).order_by('-taken_at')

#     try:
#         profile = StudentProfile.objects.get(user=request.user)
#         quizzes = Quiz.objects.filter(
#             school_class=profile.school_class,
#             arm=profile.arm
#         )
#     except StudentProfile.DoesNotExist:
#         quizzes = Quiz.objects.none()

#     return render(request, 'dashboard.html', {
#         'attempts': attempts,
#         'quizzes': quizzes
#     })

# from django.contrib.admin.views.decorators import staff_member_required

# @staff_member_required
# def class_results(request):
#     school_class = request.GET.get('class')
#     arm = request.GET.get('arm')

#     attempts = Attempt.objects.all()

#     if school_class:
#         attempts = attempts.filter(school_class__id=school_class)

#     if arm:
#         attempts = attempts.filter(arm__id=arm)

#     classes = SchoolClass.objects.all()
#     arms = ClassArm.objects.all()

#     return render(request, 'class_results.html', {
#         'attempts': attempts,
#         'classes': classes,
#         'arms': arms
#     })


# from django.contrib.auth.decorators import login_required
# from django.contrib.auth import logout
# from django.shortcuts import get_object_or_404, redirect
# from .models import Quiz, Attempt
# import time

# @login_required
# @login_required
# def end_exam(request, quiz_id):
#     quiz = get_object_or_404(Quiz, id=quiz_id)

#     attempt = Attempt.objects.filter(
#         user=request.user,
#         quiz=quiz
#     ).order_by("-taken_at").first()

#     # ✅ Save duration safely
#     if attempt and attempt.duration_seconds is None:
#         start_time = request.session.get("exam_start_time")
#         if start_time:
#             attempt.duration_seconds = int(time.time() - start_time)
#             attempt.save()

#     # 🔹 Clear per-quiz session data
#     request.session.pop("exam_start_time", None)
#     request.session.pop("answers", None)
#     request.session.pop("current_index", None)
#     request.session.pop("question_ids", None)
#     request.session.pop("current_quiz", None)

#     # ================================
#     # ✅ MULTI-SUBJECT LOGIC (SAFE)
#     # ================================
#     selected_quizzes = request.session.get("selected_quizzes")
#     current_index = request.session.get("current_quiz_index", 0)

#     if selected_quizzes:
#         current_index += 1

#         # ▶ Move to next selected subject
#         if current_index < len(selected_quizzes):
#             request.session["current_quiz_index"] = current_index
#             next_quiz_id = int(selected_quizzes[current_index])
#             return redirect("start_quiz", quiz_id=next_quiz_id)

#         # 🧹 All subjects completed → cleanup
#         request.session.pop("selected_quizzes", None)
#         request.session.pop("current_quiz_index", None)

#     # ================================
#     # 🔚 FINAL END (SINGLE OR MULTI)
#     # ================================
#     logout(request)
#     return redirect("login")

# # def end_exam(request, quiz_id):
#     # quiz = get_object_or_404(Quiz, id=quiz_id)
# # 
#     # attempt = Attempt.objects.filter(
#         # user=request.user,
#         # quiz=quiz
#     # ).order_by("-taken_at").first()
# # 
#     # if attempt and attempt.duration_seconds is None:
#         # attempt.duration_seconds = int(time.time() - request.session.get("exam_start_time", time.time()))
#         # attempt.save()
# # 
#     # Clear exam session
#     # request.session.pop("exam_start_time", None)
#     # request.session.pop("answers", None)
# # 
#     # Logout student
#     # logout(request)
# # 
#     # return redirect("login")  # change if your login URL name is differen
# from django.contrib.admin.views.decorators import staff_member_required
# from django.shortcuts import render
# from django.http import HttpResponse
# import csv
# from .models import Attempt, SchoolClass


# # @staff_member_required
# from django.contrib.admin.views.decorators import staff_member_required
# from django.http import HttpResponse
# from django.shortcuts import render
# import csv

# @staff_member_required
# def class_based_quiz_result(request):
#     classes = SchoolClass.objects.all()
#     quizzes = Quiz.objects.all()   # ✅ SUBJECTS (QUIZZES)

#     selected_class = request.GET.get("class")
#     selected_quiz = request.GET.get("quiz")

#     attempts = Attempt.objects.select_related(
#         "user",
#         "quiz",
#         "user__studentprofile",
#         "user__studentprofile__school_class"
#     )

#     # ✅ FILTER BY CLASS
#     if selected_class:
#         attempts = attempts.filter(
#             user__studentprofile__school_class__id=selected_class
#         )

#     # ✅ FILTER BY SUBJECT (QUIZ)
#     if selected_quiz:
#         attempts = attempts.filter(quiz__id=selected_quiz)

#     # 📥 DOWNLOAD CSV (CLASS + SUBJECT)
#     if "download" in request.GET:
#         response = HttpResponse(content_type="text/csv")
#         response["Content-Disposition"] = "attachment; filename=class_subject_results.csv"
#         writer = csv.writer(response)

#         writer.writerow(["Class", "Student", "Subject", "Score", "Total Marks"])

#         for a in attempts:
#             writer.writerow([
#                 a.user.studentprofile.school_class.name,
#                 a.user.username,
#                 a.quiz.title,
#                 a.score,
#                 a.total_marks
#             ])
#         return response

#     return render(request, "class_based_quiz_result.html", {
#         "attempts": attempts,
#         "classes": classes,
#         "quizzes": quizzes,
#         "selected_class": selected_class,
#         "selected_quiz": selected_quiz,
#     })
