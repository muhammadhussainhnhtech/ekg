from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serilizer import QuestionsSerilizer
import random
from .usable import preprocess_questions,calculate_probabilities
from django.conf import settings
import pandas as pd
from pathlib import Path
import os
from django.db.models import F
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent




# Create your views here.
# class anlaysis_symtoms(APIView):
#     def get(self,request):
#         try:
#             data = DiseaseSymtoms.objects.all()
#             my_list = list(data)  # convert queryset to list

#             random_indices = random.sample(range(len(my_list)), len(my_list))  # generate random indices
#             random_items = [my_list[i] for i in random_indices]  # create new list with random items

#             serilize_data = symtomsSerilizer(random_items,many=True)
#             return Response({
#                 "status": True,
#                 "data":serilize_data.data
#             })
        
#         except Exception as e:
#             message = {'status':False}
#             message.update(message=str(e))if settings.DEBUG else message.update(message='Internal server error')
#             return Response(message,status=500)
        

    
#     def post(self, request):
#         try:
#             data = request.data["questions"]
#             if not data:
#                 return Response({"status":False,"message":"Please choose atleast one question"})
            
#             else:
#                 fetchdata = DiseaseSymtoms.objects.filter(uid__in = data)
#                 summary = preprocess_questions(fetchdata)
#                 return Response({
#                     "status":True,
#                     "data":summary
#                 })
            


#         except Exception as e:
#             message = {'status':False}
#             message.update(message=str(e))if settings.DEBUG else message.update(message='Internal server error')
#             return Response(message,status=500)




class dummydata(APIView):
    def get(self,request):
        try:
            action = request.GET.get('action')
            if action == "disease":
                bulklist = list()
                diseasesnames  = ['Infarct', 'Ischemia', 'Aortic Dissection', 'PE', 'CHF', 'Pericarditis', 'AS/AI', 'Pulmonary', 'Eso rupture', 'MS', 'GI']

                getQuestions = Questions.objects.all()
                for j in diseasesnames:
                    for k in getQuestions:

                
                        bulklist.append(
                            diseases(name = j,question = k)
                        )

                diseases.objects.bulk_create(bulklist)
                return Response({"status":True,"message":"Disease and Questions inserted successfully"})    
            
            
            
            else:
                file = pd.read_csv(BASE_DIR / "symtoms/symtoms.csv")
                quest = file["question"].unique()
                fileColumns = file.columns
                totaldisease = fileColumns[2::]
                bulklist = list()
                for j in quest:
                    filterdata = file[file["question"] == j]
                    
                    for i in range(len(totaldisease)):
                        specificdiseaseSymtoms = filterdata[totaldisease[i]]
        
                        ##fetch disease data
                        fetchspecificDiseases = diseases.objects.get(name = totaldisease[i],question__question = j,question__version_list = "v1")

                        


                        for k in range(len(specificdiseaseSymtoms)):
                            bulklist.append(symtoms(name = filterdata["Chest Pain"].iloc[k],probability = specificdiseaseSymtoms.iloc[k],diseasesname = fetchspecificDiseases))
                            
                        


                symtoms.objects.bulk_create(bulklist)
                return Response({"status":True,"message":"Insertion successfully"})



        except Exception as e:
            message = {'status':False}
            message.update(message=str(e))if settings.DEBUG else message.update(message='Internal server error')
            return Response(message,status=500)






class anlaysis_symtoms(APIView):
    def get(self,request):
        try:
            action = request.GET.get('action')
            if action == 'v1':
                fetchQuestions = Questions.objects.values('id','version_list','question')
                for j in fetchQuestions:
                    #fetch symtoms according to questions
                    fetchsymtoms = symtoms.objects.filter(diseasesname__question__id = j['id']).values_list('name',flat=True).distinct()
                    j['symtoms'] = fetchsymtoms

                return Response({
                    "status": True,
                    "data":fetchQuestions

                })
            
            else:
                return Response({
                    "status":False,
                    "message":"Comming Soon...."
                })
                
        


        except Exception as e:
            message = {'status':False}
            message.update(message=str(e))if settings.DEBUG else message.update(message='Internal server error')
            return Response(message,status=500)


    def post(self, request):
        try:
            action = request.GET.get('action')
            if action == 'v1':
                data = request.data
                symtomslist = list()
                for j in data:
                    ## fetch symtoms
                    fetchSymtoms = symtoms.objects.filter(name = j["symtoms"],diseasesname__question__id =j["id"]).values('probability',diseases_name = F('diseasesname__name'))

                    symtomslist.append(
                        {   "symtomsname":j["symtoms"],
                            "symtomslist":fetchSymtoms
                            
                        }

                    )
                
                #calculate probabilities for each diseases
                symtomsSum = calculate_probabilities(symtomslist)
                return Response({
                    "status":True,
                    "data":symtomsSum
                })
            

                        
            else:
                return Response({
                    "status":False,
                    "message":"Comming Soon...."
                })
                    

        except Exception as e:
            message = {'status':False}
            message.update(message=str(e))if settings.DEBUG else message.update(message='Internal server error')
            return Response(message,status=500)