# Generated by Django 3.2.5 on 2023-09-12 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundoorAPI', '0012_remove_project_is_hero'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='hsh',
            field=models.CharField(default='0x', max_length=100),
        ),
    ]