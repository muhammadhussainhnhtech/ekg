from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serilizer import QuestionsSerilizer
import random
from .usable import preprocess_questions
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
            for j in quest:
                filterdata = file[file["question"] == j]
                print("length",len(filterdata))
                for i in range(len(totaldisease)):
                    specificdiseaseSymtoms = filterdata[totaldisease[i]]
                    print('question',totaldisease[i])
                    #print("values",specificdiseaseSymtoms)
                   
                    # for k in specificdiseaseSymtoms:
                    #     print("probability",k)

                    for k in range(len(specificdiseaseSymtoms)):
                        print("probability",k,specificdiseaseSymtoms.iloc[k],filterdata["Chest Pain"].iloc[k])


                    print('------------------------------------------')
                    
                        
                        


                   
                    #print(filterdata[i == i])

                    ##filter disease 

                    #filterdisease = diseases.objects.filter()


                   

            
            



           
            return Response('okay')







            # bulklist = []
            # symptomslist = ['Pressure', 'Squeezing', 'Central', 'Gripping', 'Heaviness', 'Tightness', 'Exertional', 'Retrosternal', 'Left side', 'Dull', 'Ache', 'Stabbing', 'Right side', 'Tearing', 'Ripping', 'Burning', 'Boring', 'Sharp', 'Pleuritic', 'Positional', 'Fleeting', 'Radiates', 'Jaw', 'Left arm', 'Right arm', 'Sudden', 'Gradual', 'Severe', 'Subacute', 'Onset at rest', 'Sweating', 'Nitrate relief', 'Fever', 'Cough', 'Short of breath', 'Localised', 'Radiating to Back', 'Stomach', 'Tender', 'Throat', 'Diffuse', 'Splitting', 'Seconds', 'Minutes', 'Hours', 'Days', 'Weeks', 'Months', 'Years', 'Nausea', 'Vomiting', 'Syncope', 'Acid reflux', 'Improvement with Bending', 'Persistent', 'Intermittent', 'Eating']
            
            
            # getdiseases = diseases.objects.all()

            # for j in symptomslist:
            #     for k in getdiseases:
            #         bulklist.append(

            #             symtoms()
            #         )

            # symtoms.objects.bulk_create(bulklist)


            
        