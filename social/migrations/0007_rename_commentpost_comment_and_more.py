# Generated by Django 4.1.3 on 2022-11-15 14:56

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('social', '0006_commentpost_parent'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CommentPost',
            new_name='Comment',
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='comment_post',
            new_name='comment',
        ),
    ]
