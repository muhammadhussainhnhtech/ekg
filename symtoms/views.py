from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serilizer import symtomsSerilizer
import random
from .usable import preprocess_questions
from django.conf import settings

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
        

    
    def post(self, request):
        try:
            data = request.data["questions"]
            if not data:
                return Response({"status":False,"message":"Please choose atleast one question"})
            
            else:
                fetchdata = DiseaseSymtoms.objects.filter(uid__in = data)
                summary = preprocess_questions(fetchdata)
                return Response({
                    "status":True,
                    "data":summary
                })
            


        except Exception as e:
            message = {'status':False}
            message.update(message=str(e))if settings.DEBUG else message.update(message='Internal server error')
            return Response(message,status=500)