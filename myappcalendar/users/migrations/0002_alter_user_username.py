# Generated by Django 4.0.4 on 2022-06-01 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(default='Unknown', max_length=50, unique=True),
        ),
    ]
