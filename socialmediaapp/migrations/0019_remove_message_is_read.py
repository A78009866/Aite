# Generated by Django 5.1.6 on 2025-03-24 17:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialmediaapp', '0018_message_is_read'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='is_read',
        ),
    ]
