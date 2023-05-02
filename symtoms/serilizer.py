from .models import *
from rest_framework import serializers

class QuestionsSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        exclude = ('created_at','updated_at')