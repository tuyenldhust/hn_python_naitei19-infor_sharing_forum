# Generated by Django 4.2.5 on 2023-10-04 17:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_remove_notification_user_notification_action_user_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-created_at']},
        ),
    ]