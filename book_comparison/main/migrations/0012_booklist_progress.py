# Generated by Django 5.1.1 on 2024-10-29 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_rename_book_booklist_book_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='booklist',
            name='progress',
            field=models.IntegerField(default=0),
        ),
    ]
