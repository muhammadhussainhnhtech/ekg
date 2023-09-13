from django.db import models
import uuid
# Create your models here.



class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,max_length=255)
    updated_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True,blank=True, null=True)



    class Meta:
        abstract = True

class Questions(BaseModel):

    versionList = (
        ('v1', 'v1'),
        ('v2', 'v2'),
        ('v3', 'v3'),
        ('v4', 'v4'),
        ('v5', 'v5'),
        ('v6', 'v6'),
        ('v7', 'v7'),
        ('v8', 'v8'),

    )


    version_list = models.CharField(max_length=5, choices=versionList,null=False, blank=False)
    question = models.TextField( null=False, blank=False)


    def __str__(self):
        return self.question




class diseases(BaseModel):
    name =  models.CharField(max_length=255,null=False, blank=False)
    probability = models.FloatField(null=False, blank=False) ##prior probability
    question = models.ForeignKey(Questions,on_delete=models.CASCADE,blank=False,null=False)


    def __str__(self):
        return self.name




class symtoms(BaseModel):
    name = models.CharField(max_length=255,null=False, blank=False)
    probability = models.FloatField(null=False, blank=False) ##likelyhood probability
    diseasesname = models.ForeignKey(diseases,on_delete=models.CASCADE,blank=False,null=False)


    def __str__(self):
        return self.name


class Diagnosticinfo(BaseModel):
    name =  models.CharField(max_length=255,null=False, blank=False)
    diagnostic_test = models.TextField(null=False, blank=False)

    def __str__(self):
        return self.name