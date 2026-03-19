from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import calendar



User = get_user_model()


# ============================
# SUBJECT
# ============================

class Subject(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


# ============================
# ACADEMIC STRUCTURE
# ===========================
class SchoolClass(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name
class ClassArm(models.Model):
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name='arms'
    )

    name = models.CharField(max_length=20)

    class Meta:
        unique_together = ('school_class', 'name')

    def __str__(self):
        return f"{self.school_class} - {self.name}"


# ============================
# QUIZ
# ============================
class Quiz(models.Model):
    title = models.CharField(max_length=200)

    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Class
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Multiple arms
    arms = models.ManyToManyField(ClassArm, blank=True)

    time_limit = models.PositiveIntegerField(
        help_text='Time limit in minutes',
        default=10
    )

    total_questions = models.PositiveIntegerField(default=10)
       
    

    def __str__(self):
        return self.title


# ============================
# QUESTION
# ============================

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    passage = models.TextField(blank=True, null=True)
    text = models.TextField()
    marks = models.PositiveIntegerField(default=1)
    explanation = models.TextField(blank=True, null=True)


    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)

    correct_option = models.CharField(
        max_length=1,
        choices=[
            ('A', 'Option A'),
            ('B', 'Option B'),
            ('C', 'Option C'),
            ('D', 'Option D'),
        ]
    )
    
    
    # ✅ OPTIONAL IMAGE FOR ANY QUESTION
    image = models.ImageField(
        upload_to='question_images/',
        blank=True,
        null=True
    )


    def __str__(self):
        return self.text[:60]


# ============================
# ATTEMPT
# ============================

class Attempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)

    # Snapshot of class at exam time
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    arm = models.ForeignKey(
        ClassArm,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    score = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=0)
    taken_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.quiz}"

# ============================
# STUDENT PROFILE
# ============================
from django.utils import timezone

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.SET_NULL,
        null=True
    )

    arm = models.ForeignKey(
        ClassArm,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # ✅ FREE TRIAL FIELDS
    trial_start_time = models.DateTimeField(null=True, blank=True)
    trial_used = models.BooleanField(default=False)  # IMPORTANT
    trial_duration_minutes = models.IntegerField(default=9)

    def trial_active(self):
        if not self.trial_start_time:
            return False
        end_time = self.trial_start_time + timezone.timedelta(minutes=self.trial_duration_minutes)
        return timezone.now() < end_time

    def __str__(self):
        return f"{self.user.username} ({self.school_class} {self.arm or ''})"

class Subscription(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    receipt = models.ImageField(upload_to='receipts/', null=True, blank=True)

    billing_day = models.IntegerField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='expired')

    def activate(self):
        now = timezone.now()

        if not self.billing_day:
            self.billing_day = now.day
            self.start_date = now
            self.end_date = self._calculate_next_expiry(now)

        else:
            if self.end_date and self.end_date > now:
                pass
            else:
                self.end_date = self._calculate_next_expiry(now)

        self.status = "active"
        self.save()

    def _calculate_next_expiry(self, reference_date):
        next_month = reference_date + relativedelta(months=1)

        year = next_month.year
        month = next_month.month
        last_day = calendar.monthrange(year, month)[1]

        day = min(self.billing_day, last_day)

        return next_month.replace(day=day)

    def is_active(self):
        if self.status == "active" and self.end_date and self.end_date > timezone.now():
            return True
        else:
            self.status = "expired"
            self.save()
            return False

    def __str__(self):
        return self.user.username
    


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    
    
# ---------------- Study Material ---------------
class StudyMaterial(models.Model):
    
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    topic = models.CharField(max_length=200)

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE
    )

    arms = models.ManyToManyField(
        ClassArm,
        blank=True
    )

    pdf = models.FileField(
        upload_to='study_materials/',
        blank=True,
        null=True
    )

    video_link = models.URLField(
        blank=True,
        null=True
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject.name} - {self.topic}"

    def get_embed_video_url(self):
        if not self.video_link:
            return ""

        url = self.video_link.strip()

        # YOUTUBE
        if "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]
            return f"https://www.youtube.com/embed/{video_id}"

        elif "watch?v=" in url:
            video_id = url.split("watch?v=")[1].split("&")[0]
            return f"https://www.youtube.com/embed/{video_id}"

        # VIMEO
        elif "vimeo.com/" in url:
            video_id = url.split("vimeo.com/")[1].split("/")[0]
            return f"https://player.vimeo.com/video/{video_id}"

        return ""