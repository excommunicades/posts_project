# Generated by Django 5.1.2 on 2024-10-18 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_blocked',
            field=models.BooleanField(default=False),
        ),
    ]
