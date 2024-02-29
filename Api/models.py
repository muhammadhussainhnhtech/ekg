from django.db import models
import uuid
# Create your models here.

class DropDown(models.Model):

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name=models.CharField(max_length=255, default="")
    dropdownname=models.CharField(max_length=255, default="")
    updated_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)

    def __str__(self):
        return self.name