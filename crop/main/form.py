from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Desease
from tinymce.widgets import TinyMCE
from django.db import models
from django import forms

class CreateUserFrom(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']


class DiseaseForm(ModelForm):
    class Meta:
        model = Desease
        fields = '__all__'
