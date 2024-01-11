import os
import uuid

from django.utils.text import slugify


def train_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    return os.path.join(
        "uploads/trains/",
        f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"
    )
