from django.shortcuts import render,HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from PIL import Image
import numpy as np
#from .loadingmodel import *
from collections import Counter
from .models import *
from random import random





class getdropdowndata(APIView):

    def get(self, request):

        return Response({"status":True,"data":DropDown.objects.values('name','dropdownname')})



class prediction(APIView):

    def post(self,request):

        # try:

        image = request.FILES.getlist('image')
        modelname = request.data.get('model')
       
        if not image:
            return Response({'status':False,'message':"Image in required"}) 

        if not modelname:
            return Response({'status':False,'message':"Please Select Heart Category"}) 

     
        

        if modelname == "dis":
            predictionLabels = [
                {'name':'Atrial flutter','colour':'rgba(255, 99, 132)','percent':0},
                {'name':'Sinus bradycardia','colour':'rgba(54, 162, 235)','percent':0},
                {'name':'Sinus tachycardia','colour':'rgba(244, 2, 62)','percent':0},
            ]
           
            sample = np.load(image[0]).reshape(5000,12)
            sample = np.array([sample])
            Pr = model3.predict(sample)[0]

            for i in range(len(predictionLabels)):
                percentage_value = Pr[i] * 100
                percentage_string = f"{percentage_value:.2f}"
                predictionLabels[i]['percent'] = percentage_string
    

          
            return Response({"status":True,"message":"Success","data":predictionLabels})
        

        if modelname == "cd":
            predictionLabels = [
                {'name':'IAVB','colour':'rgba(255, 99, 132)','percent':0},
                {'name':'LAnFB','colour':'rgba(54, 162, 235)','percent':0}
            ]
           
            sample = np.load(image[0]).reshape(5000,12)
            sample = np.array([sample])
            Pr = model4.predict(sample)[0]

            for i in range(len(predictionLabels)):
                percentage_value = Pr[i] * 100
                percentage_string = f"{percentage_value:.2f}"
                predictionLabels[i]['percent'] = percentage_string
    

          
            return Response({"status":True,"message":"Success","data":predictionLabels})

        
        if modelname == "sttc":
            predictionLabels = [
                {'name':'NSSTTA','colour':'rgba(255, 99, 132)','percent':0},
                {'name':'STD','colour':'rgba(54, 162, 235)','percent':0}
            ]
           
            sample = np.load(image[0]).reshape(5000,12)
            sample = np.array([sample])
            Pr = model2.predict(sample)[0]

            for i in range(len(predictionLabels)):
                percentage_value = Pr[i] * 100
                percentage_string = f"{percentage_value:.2f}"
                predictionLabels[i]['percent'] = percentage_string
    

          
            return Response({"status":True,"message":"Success","data":predictionLabels})

        
        if modelname == "hyp":
            predictionLabels = [
                {'name':'left atrial enlargement','colour':'rgba(255, 99, 132)','percent':0},
                {'name':'left ventricular hypertrophy','colour':'rgba(54, 162, 235)','percent':0}
            ]
           
            sample = np.load(image[0]).reshape(5000,12)
            sample = np.array([sample])
            Pr = model1.predict(sample)[0]

            for i in range(len(predictionLabels)):
                percentage_value = Pr[i] * 100
                percentage_string = f"{percentage_value:.2f}"
                predictionLabels[i]['percent'] = percentage_string
    

          
            return Response({"status":True,"message":"Success","data":predictionLabels})

        

        if modelname == "mi":
            predictionLabels = [
                {'name':'Acute myocardial','colour':'rgba(255, 99, 132)','percent':0},
                {'name':'OldMI','colour':'rgba(54, 162, 235)','percent':0}
            ]
           
            sample = np.load(image[0]).reshape(5000,12)
            sample = np.array([sample])
            Pr = model5.predict(sample)[0]

            for i in range(len(predictionLabels)):
                percentage_value = Pr[i] * 100
                percentage_string = f"{percentage_value:.2f}"
                predictionLabels[i]['percent'] = percentage_string
    

          
            return Response({"status":True,"message":"Success","data":predictionLabels})

        


        
       
        
       