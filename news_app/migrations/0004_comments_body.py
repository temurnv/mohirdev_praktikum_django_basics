# Generated by Django 3.2.25 on 2024-06-05 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_app', '0003_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='comments',
            name='body',
            field=models.TextField(blank=True, null=True),
        ),
    ]
