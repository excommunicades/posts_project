# Generated by Django 5.1.2 on 2024-10-18 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_post_is_blocked'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='auto_reply_delay',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='auto_reply_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='post',
            name='auto_reply_text',
            field=models.TextField(blank=True, null=True),
        ),
    ]