# Generated by Django 3.2.5 on 2023-08-22 23:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundoorAPI', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='currency',
        ),
        migrations.AddField(
            model_name='project',
            name='currency',
            field=models.ManyToManyField(to='fundoorAPI.Currency'),
        ),
    ]
