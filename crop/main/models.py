from django.db import models

class Desease(models.Model):
    Disease_name = models.CharField(max_length = 200)
    Disease_description = models.TextField()
    
    Disease_healthy_picture = models.ImageField(null = True, blank = True)
    Disease_unhealthy_picture = models.ImageField(null = True, blank = True)
    
    Disease_symptoms = models.TextField()
    Disease_remidies = models.TextField()


    def __str__(self):
        return self.Disease_name

class imageSearch(models.Model):
    uploaded_image = models.ImageField()