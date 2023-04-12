from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serilizer import symtomsSerilizer
import random

# Create your views here.
class anlaysis_symtoms(APIView):
    def get(self,request):
        try:
            data = DiseaseSymtoms.objects.all()
            my_list = list(data)  # convert queryset to list

            random_indices = random.sample(range(len(my_list)), len(my_list))  # generate random indices
            random_items = [my_list[i] for i in random_indices]  # create new list with random items

            serilize_data = symtomsSerilizer(random_items,many=True)
            return Response({
                "status": True,
                "data":serilize_data.data
            })
        
        except Exception as e:
            message = {'status':False}
            message.update(message=str(e))if settings.DEBUG else message.update(message='Internal server error')
            return Response(message,status=500)