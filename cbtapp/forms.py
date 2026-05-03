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
from .models import StudentProfile, ClassArm


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


# ========================================
# CUSTOM SELECT WIDGET FOR CLASS ARM
# ========================================
class ClassArmSelectWidget(forms.Select):
    """
    Custom widget that adds data-school-class attribute to each option
    """
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        
        # Add data-school-class attribute to each option
        if value:
            try:
                # Extract the actual ID from the value object
                actual_value = value.value if hasattr(value, 'value') else value
                
                if actual_value:  # Make sure it's not empty string or None
                    class_arm = ClassArm.objects.get(pk=actual_value)
                    option['attrs']['data-school-class'] = str(class_arm.school_class.id)
            except (ClassArm.DoesNotExist, AttributeError, ValueError):
                pass
        
        return option


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['school_class', 'arm']
        widgets = {
            'arm': ClassArmSelectWidget(),  # Use custom widget for filtering
        }