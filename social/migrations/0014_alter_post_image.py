# Generated by Django 4.1.3 on 2022-11-22 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0013_delete_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/post_photos'),
        ),
    ]
