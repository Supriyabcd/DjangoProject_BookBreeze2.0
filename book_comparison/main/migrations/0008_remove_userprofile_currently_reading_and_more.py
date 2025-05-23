# Generated by Django 5.1.2 on 2024-10-25 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_userprofile_currently_reading_userprofile_read_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='currently_reading',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='read',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='want_to_read',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='currently_reading',
            field=models.ManyToManyField(blank=True, related_name='currently_reading_users', to='main.book'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='read',
            field=models.ManyToManyField(blank=True, related_name='read_users', to='main.book'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='want_to_read',
            field=models.ManyToManyField(blank=True, related_name='want_to_read_users', to='main.book'),
        ),
    ]
