# Generated by Django 4.2.3 on 2023-08-22 22:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_remove_subscribe_unique_name_follower_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="subscribe",
            name="uq_user_following",
        ),
        migrations.RenameField(
            model_name="subscribe",
            old_name="following",
            new_name="author",
        ),
        migrations.AddConstraint(
            model_name="subscribe",
            constraint=models.UniqueConstraint(
                fields=("user", "author"), name="uq_user_author"
            ),
        ),
    ]