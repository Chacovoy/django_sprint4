# Generated by Django 3.2.16 on 2023-09-02 11:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_rename_post_comment_blog_post'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='blog_post',
            new_name='post',
        ),
    ]
