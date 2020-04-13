from django.db import models
from django.contrib.auth import get_user_model


class Course(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    teacher = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING)
    subject = models.CharField(default='', max_length=100)
    published = models.BooleanField(default=False)

    def __str__(self):
        return self.title
