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
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import StudentRegisterForm, StudentProfileForm
import pandas as pd
from django.contrib import messages
from .models import Quiz, Question, Subject
from .forms import BulkQuestionUploadForm
from django.contrib.auth.decorators import login_required
from .models import Subscription
from django.shortcuts import render, redirect
from .models import Subscription, StudentProfile, Quiz, Attempt
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import StudyMaterial
import random
from django.conf import settings
from django.http import FileResponse, Http404
import os
from django.conf import settings





def home(request):
    return render(request, 'home.html')
def pricing(request):
    return render(request, 'pricing.html')

def about(request):
    return render(request, 'about.html')

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
@login_required
def dashboard(request):
    profile = StudentProfile.objects.get(user=request.user)

    # ───────── FREE TRIAL LOGIC ─────────
    if not profile.trial_used:
        if profile.trial_start_time is None:
            profile.trial_start_time = timezone.now()
            profile.trial_used = True
            profile.save()

    trial_active = profile.trial_active()

    # ───────── SUBSCRIPTION CHECK ─────────
    subscription = Subscription.objects.filter(user=request.user).first()
    access_allowed = False

    if subscription and subscription.is_active():
        access_allowed = True

    # 🚫 BLOCK ACCESS
    if not access_allowed and not trial_active:
        return redirect('subscribe')

    # ───────── FETCH DATA ─────────
    quizzes = Quiz.objects.filter(
        school_class=profile.school_class,
        arms__in=[profile.arm]
    ).distinct()

    materials = StudyMaterial.objects.filter(
        school_class=profile.school_class,
        arms__in=[profile.arm]
    ).distinct()

    attempts = Attempt.objects.filter(user=request.user).order_by('-taken_at')

    # ───────── DAYS LEFT ─────────
    days_left = None
    if subscription and subscription.end_date:
        delta = subscription.end_date - timezone.now()
        days_left = max(delta.days, 0)

    # ───────── CONTEXT ─────────
    context = {
        "quizzes": quizzes,
        "attempts": attempts,
        "subscription": subscription,
        "days_left": days_left,
        "materials": materials,
        "trial_active": trial_active,
        "trial_end_time": (
            profile.trial_start_time + timezone.timedelta(minutes=profile.trial_duration_minutes)
            if profile.trial_start_time else None
        )
    }

    return render(request, "dashboard.html", context)
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

                # Create Attempt
                attempt = Attempt.objects.create(
                    user=request.user,
                    quiz=quiz,
                    school_class=profile.school_class,
                    arm=profile.arm,
                )

                # Save attempt id in session
                request.session[attempt_key] = attempt.id

                # ====== SHUFFLE QUESTIONS ======
                questions = list(Question.objects.filter(quiz=quiz))
                random.shuffle(questions)
                request.session[f"shuffled_questions_{quiz_id}"] = [q.id for q in questions]

            except StudentProfile.DoesNotExist:
                questions = Question.objects.filter(quiz=quiz)
        else:
            # Load shuffled questions from previous session
            question_ids = request.session.get(f"shuffled_questions_{quiz_id}")
            if question_ids:
                questions = Question.objects.filter(id__in=question_ids)
                # Maintain the order
                questions = sorted(questions, key=lambda q: question_ids.index(q.id))
            else:
                questions = list(Question.objects.filter(quiz=quiz))
    else:
        questions = list(Question.objects.filter(quiz=quiz))

    if not questions:
        return render(request, "no_questions.html")

    # =========================
    # Handle question index & answers
    # =========================
    question_indexes = request.session.get("question_indexes", {})
    index = question_indexes.get(str(quiz_id), 0)
    answers = request.session.get("answers", {})

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
    # Timer
    # =========================
    remaining_seconds = None
    start_time_str = request.session.get("start_time")
    total_exam_seconds = request.session.get("total_exam_seconds")
    if start_time_str and total_exam_seconds:
        start_time = timezone.datetime.fromisoformat(start_time_str)
        elapsed = (timezone.now() - start_time).total_seconds()
        remaining_seconds = max(0, int(total_exam_seconds - elapsed))
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
        "total_questions": len(questions),
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



def view_pdf(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)

    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    raise Http404()