# Generated by Django 2.2.16 on 2021-01-27 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authuser',
            name='avatar_url',
            field=models.CharField(max_length=1024, null=True),
        ),
    ]