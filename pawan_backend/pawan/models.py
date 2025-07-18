from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
# Create your models here.

class PawanUser(AbstractUser):
    email_token = models.UUIDField(default=uuid.uuid4)
    is_verified = models.BooleanField(default = False)
    def __str__(self):
        return self.username
