# Generated by Django 3.0.3 on 2021-01-26 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_remove_desease_disease_display_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='desease',
            name='Disease_healthy_picture',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='desease',
            name='Disease_unhealthy_picture',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]