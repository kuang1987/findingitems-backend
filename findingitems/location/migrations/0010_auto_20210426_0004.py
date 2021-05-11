# Generated by Django 2.2.16 on 2021-04-25 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0009_locationmemberinvitation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locationmemberinvitation',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'pending'), (1, 'confirm'), (2, 'reject')], default=0),
        ),
    ]