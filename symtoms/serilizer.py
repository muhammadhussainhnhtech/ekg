from .models import *
from rest_framework.serializers import ModelSerializer,CharField,Serializer,EmailField
from passlib.hash import django_pbkdf2_sha256 as handler
from django.core.validators import RegexValidator

class QuestionsSerilizer(ModelSerializer):
    class Meta:
        model = Questions
        exclude = ("created_at", "updated_at")

class FeedbackSerializer(ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

class AuthSerializer(ModelSerializer):
    fname = CharField(
        max_length=255,
        required=False,
        #validators=[RegexValidator(r'^[a-zA-Z]*$', 'First name must contain only alphabetical characters.')]
    )
    lname = CharField(
        max_length=255,
        required=False,
        #validators=[RegexValidator(r'^[a-zA-Z]*$', 'Last name must contain only alphabetical characters.')]
    )
    password = CharField(
        write_only=True,
        min_length=8,
        max_length=16,
        error_messages={
            'min_length': 'Password must be at least 8 characters long.'
        }
    )
    class Meta:
        model = Auth
        fields = ["id",'fname', 'lname', 'email',"password"]



    class Meta:
        model = Auth
        fields = '__all__'

    def validate(self, data):
        data['password'] = handler.hash(data['password'])
        return data

class LoginSerializer(Serializer):
    email = EmailField(required=True)
    password = CharField(required=True, write_only=True,min_length=8, max_length=16)