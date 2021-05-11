# Generated by Django 2.2.16 on 2021-02-26 07:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0001_initial'),
        ('instruction', '0004_instruction_is_delete'),
    ]

    operations = [
        migrations.AddField(
            model_name='instruction',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='instructions', to='location.Location'),
        ),
    ]