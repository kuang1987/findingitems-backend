# Generated by Django 2.2.16 on 2021-02-03 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instruction', '0003_auto_20210203_0036'),
    ]

    operations = [
        migrations.AddField(
            model_name='instruction',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
    ]