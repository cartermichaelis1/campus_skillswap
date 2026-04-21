from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from datetime import date as date_cls
from .models import Skill, Review, Appointment


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'username': 'Choose a username',
            'email': 'your@university.edu',
            'password1': 'Create a strong password',
            'password2': 'Confirm your password',
        }
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[field_name]


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['title', 'description', 'category', 'price_type', 'contact_info']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Python tutoring, Guitar lessons, Logo design...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe your skill, your experience level, what students can expect...'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price_type': forms.Select(attrs={'class': 'form-select'}),
            'contact_info': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. email@uni.edu, @discord_handle, Instagram...'
            }),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your experience with this skill...'
            }),
        }


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'message']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any details, questions, or location preferences...'
            }),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < date_cls.today():
            raise forms.ValidationError('Please choose a date in the future.')
        return date
