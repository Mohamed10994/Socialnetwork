# Generated by Django 4.1.3 on 2022-11-17 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0011_notification_thread'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='uploads/post_photos')),
            ],
        ),
    ]
