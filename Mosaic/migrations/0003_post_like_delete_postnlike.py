# Generated by Django 4.2.4 on 2023-12-21 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Mosaic', '0002_postnlike_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='like',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
        migrations.DeleteModel(
            name='PostnLike',
        ),
    ]
