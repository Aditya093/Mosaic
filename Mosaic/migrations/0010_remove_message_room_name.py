# Generated by Django 3.2.5 on 2023-12-24 13:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Mosaic', '0009_message_room_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='room_name',
        ),
    ]
