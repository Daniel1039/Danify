from django.contrib import admin
from .models import Subject, Quiz, Question, Attempt, SchoolClass, ClassArm, StudentProfile
from django.urls import path
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
import csv, io
from django.contrib import admin
from .models import ContactMessage

# ---------------- Subject ----------------
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

# ---------------- SchoolClass Admin ----------------
@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('name',)

# ---------------- ClassArm Admin ----------------
@admin.register(ClassArm)
class ClassArmAdmin(admin.ModelAdmin):
    list_display = ('school_class', 'name')
    list_filter = ('school_class',)
    search_fields = ('name',)

# ---------------- StudentProfile Admin ----------------
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'school_class', 'arm')
    list_filter = ('school_class', 'arm')
    
    # ✅ Exact match (SS3 ≠ JSS3)
    search_fields = (
        'school_class__name__iexact',
    )


    # search_fields = ('user__username',
from django.contrib import admin
from .models import Quiz, Question

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = (
         'passage',
        'text', 'image', 'marks',
        'option_a', 'option_b', 'option_c', 'option_d',
        'correct_option', 'explanation',
    )

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'school_class', 'display_arms', 'time_limit', 'total_questions')
    inlines = [QuestionInline]

    def display_arms(self, obj):
        # Make sure this matches your ManyToManyField name in Quiz
        return ", ".join([arm.name for arm in obj.arms.all()])
    display_arms.short_description = 'Arms'

    # Optional: CSV import
    change_list_template = 'admin/cbtapp/quiz_changelist.html'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom = [path('import-questions/', self.admin_site.admin_view(self.import_questions))]
        return custom + urls

    def import_questions(self, request):
        import csv, io
        from django.shortcuts import redirect, render
        if request.method == 'POST':
            csvfile = request.FILES['csv_file']
            data = csvfile.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(data))
            created = 0
            for row in reader:
                quiz_title = row.get('quiz') or 'Default Quiz'
                quiz, _ = Quiz.objects.get_or_create(title=quiz_title)
                Question.objects.create(
                    quiz=quiz,
                    passage=row.get('passage', ''),
                    text=row['question_text'],
                    marks=int(row.get('marks') or 1),
                    option_a=row.get('option_a', ''),
                    option_b=row.get('option_b', ''),
                    option_c=row.get('option_c', ''),
                    option_d=row.get('option_d', ''),
                    correct_option=row.get('correct_option', 'A').upper(),
                    explanation=row.get('explanation', ''),
                )
                created += 1
            self.message_user(request, f"Imported {created} questions.")
            return redirect('..')
        context = dict(self.admin_site.each_context(request))
        return render(request, 'admin/cbtapp/import_questions.html', context)
# ---------------- Question Admin ----------------
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz')
    change_list_template = "admin/questions_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv), name='import_questions_csv'),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES.get("csv_file")
            if not csv_file:
                self.message_user(request, "No file selected")
                return redirect("..")
            if not csv_file.name.endswith(".csv"):
                self.message_user(request, "This is not a CSV file")
                return redirect("..")
            data = csv_file.read().decode("utf-8")
            io_string = io.StringIO(data)
            reader = csv.DictReader(io_string)
            created = 0
            for row in reader:
                quiz_title = row.get("quiz", "").strip()
                quiz, _ = Quiz.objects.get_or_create(title=quiz_title)
                subject_name = row.get("subject", "").strip()
                subject = Subject.objects.filter(name__iexact=subject_name).first()
                Question.objects.create(
                    quiz=quiz,
                    subject=subject,
                    text=row["question_text"],
                    option_a=row["option_a"],
                    option_b=row["option_b"],
                    option_c=row["option_c"],
                    option_d=row["option_d"],
                    correct_option=row["correct_option"].upper(),
                    marks=int(row.get("marks", 1)),
                )
                created += 1
            self.message_user(request, f"{created} questions imported successfully!")
            return redirect("..")
        context = dict(self.admin_site.each_context(request))
        return TemplateResponse(request, "admin/csv_form.html", context)

# ---------------- Attempt Admin ----------------
# @admin.register(Attempt)
# class AttemptAdmin(admin.ModelAdmin):
    # list_display = ('user', 'quiz', 'score', 'total_marks', 'taken_at')
# 

from django.contrib import admin
from .models import Attempt, Quiz, Question, Subject

@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'quiz',
        'school_class',
        'arm',
        'score',
        'total_marks',
        'taken_at'
    )
    list_filter = ('school_class', 'arm', 'quiz')
    
    # ✅ Exact match (SS3 ≠ JSS3)
    search_fields = (
        'school_class__name__iexact',
    )
    
    
from django.urls import reverse 
from django.utils.html import format_html
from django.contrib import admin

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'view_class_results_link', ...)
    
    def view_class_results_link(self, obj):
        url = reverse('class_quiz_result') + f'?quiz={obj.id}'
        return format_html('<a href="{}">View Class Results</a>', url)
    view_class_results_link.short_description = "Class Quiz Results"


from django.contrib import admin
from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'end_date')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created")
    search_fields = ("name", "email", "subject")
    list_filter = ("created",)
    readonly_fields = ("name", "email", "subject", "message", "created")