from django.db import models

class Essay(models.Model):
    """ Essay to be submitted. """
    content = models.TextField(max_length=100000)
    score = models.IntegerField(null=True, blank=True)
