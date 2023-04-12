from django.db import models
import uuid
# Create your models here.

class DiseaseSymtoms(models.Model):

    disease_options = (
        ('cardic', 'cardic'),
        ('uncardic', 'uncardic'),
    )

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField( null=False, blank=False)
    diseases_type = models.CharField(max_length=20, choices=disease_options,null=False, blank=False)
    priority = models.IntegerField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)

    def __str__(self):
        return self.question