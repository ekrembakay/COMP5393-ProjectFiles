from django.db import models
from django.contrib.auth.models import User

class Essay(models.Model):
    """ Essay to be submitted. """
    content = models.TextField(max_length=100000)
    score = models.IntegerField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
