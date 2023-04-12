from .models import *
from rest_framework import serializers

class symtomsSerilizer(serializers.ModelSerializer):
    class Meta:
        model = DiseaseSymtoms
        exclude = ('created_at','updated_at')