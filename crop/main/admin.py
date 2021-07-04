from django.contrib import admin
from .models import Desease
from tinymce.widgets import TinyMCE
from django.db import models

class desease(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }


admin.site.register(Desease,desease)