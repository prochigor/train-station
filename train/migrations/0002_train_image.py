# Generated by Django 5.0 on 2023-12-12 09:06

import train.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("train", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="train",
            name="image",
            field=models.ImageField(
                null=True, upload_to=train.models.train_image_file_path
            ),
        ),
    ]
