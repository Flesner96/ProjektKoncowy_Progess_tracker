# Generated by Django 5.0.6 on 2024-06-13 09:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('progress_tracker', '0002_remove_characterquestprogress_progress_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='character',
            name='profession',
        ),
    ]
