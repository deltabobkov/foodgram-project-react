# Generated by Django 4.2.3 on 2023-08-26 21:30

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_remove_subscribe_uq_user_following_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="subscribe",
            options={
                "verbose_name": "Подписка",
                "verbose_name_plural": "Подписки",
            },
        ),
    ]
