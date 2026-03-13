from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Question

User = get_user_model()

# ---------------- SignUp Form ----------------
class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')

# ---------------- Answer Form ----------------
class AnswerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')  # get the question object
        super().__init__(*args, **kwargs)
        self.fields['answer'] = forms.ChoiceField(
            choices=[
                ('A', question.option_a),
                ('B', question.option_b),
                ('C', question.option_c),
                ('D', question.option_d),
            ],
            widget=forms.RadioSelect,
            label=question.text
        )

# forms.py
from django import forms

class BulkQuestionUploadForm(forms.Form):
    file = forms.FileField(label="Upload CSV/Excel file")





from django import forms
from django.contrib.auth.models import User
from .models import StudentProfile


class StudentRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password != confirm:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['school_class', 'arm']