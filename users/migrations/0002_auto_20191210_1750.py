# Generated by Django 2.2.6 on 2019-12-10 17:50

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userdata',
            name='id',
        ),
        migrations.AddField(
            model_name='userdata',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userdata',
            name='pin',
            field=models.PositiveIntegerField(default=1111, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]