from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serilizer import QuestionsSerilizer
import random
from .usable import *
from django.conf import settings
import pandas as pd
from pathlib import Path
import os
from django.db.models import F
import numpy as np
from .loadingmodel import model


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


class dummydata(APIView):
    def get(self,request):
        try:
            action = request.GET.get('action',"v1")
            version = request.GET.get('version',"v1")
            if action == "disease":
                bulklist = list()
                file = pd.read_csv(BASE_DIR / "symtoms/disease.csv")
                getQuestions = Questions.objects.filter(version_list = version)
                for i,j in zip(file["Diseases"],file["probability"]):
                    for k in getQuestions:


                        bulklist.append(
                            diseases(name = i,question = k,probability = j)
                        )



                diseases.objects.bulk_create(bulklist)
                return Response({"status":True,"message":"Disease and Questions inserted successfully"})





            else:
                file = pd.read_csv(BASE_DIR / f"symtoms/{action}.csv")
                quest = file["question"].unique()
                fileColumns = file.columns
                totaldisease = fileColumns[2::]
                bulklist = list()
                for j in quest:
                    filterdata = file[file["question"] == j]

                    for i in range(len(totaldisease)):
                        specificdiseaseSymtoms = filterdata[totaldisease[i]]

                        # print(totaldisease[i])
                        # print(j)
                        # print(version)
                        # print("-----------------")
                        #fetch disease data
                        fetchspecificDiseases = diseases.objects.get(name = totaldisease[i],question__question = j,question__version_list = version)




                        for k in range(len(specificdiseaseSymtoms)):
                            #chec if already exists

                            checkif = symtoms.objects.filter(name = filterdata["Chest Pain"].iloc[k],diseasesname = fetchspecificDiseases).first()

                            if not checkif:
                                # print("if")
                                # print(filterdata["Chest Pain"].iloc[k])
                                # print(specificdiseaseSymtoms.iloc[k])
                                # print("----------------------------------------------------------------")
                                bulklist.append(symtoms(name = filterdata["Chest Pain"].iloc[k],probability = specificdiseaseSymtoms.iloc[k],diseasesname = fetchspecificDiseases))

                            else:
                                # print("else")
                                # print(checkif.name)
                                # print(checkif.probability)
                                # print("----------------------------------------------------------------")

                                checkif.probability = specificdiseaseSymtoms.iloc[k]
                                checkif.save()





                #print("finallist",bulklist)
                if bulklist:
                    symtoms.objects.bulk_create(bulklist)

                return Response({"status":True,"message":"Insertion successfully"})



        except Exception as e:
            message = {'status':False}
            message.update(message=str(e))if settings.DEBUG else message.update(message='Internal server error')
            return Response(message,status=500)







class manuplatedata(APIView):
    def get(self, request):
        try:
            allowaction = ["prior","liklyhood"]
            action = request.GET.get('action')
            name = request.GET.get('name',False)
            Symtoms = request.GET.get('symtom',False)
            probability = request.GET.get('probability',False)

            if action in allowaction and name and probability:
                if action == "prior":
                    fetchPrior = diseases.objects.filter(name = name).update(probability = probability)
                    return Response({"status":True,"message":"Prior Probability Updated"})


                else:
                    if Symtoms:
                        fetchLikly = symtoms.objects.filter(name = Symtoms,diseasesname__name = name ).update(probability = probability)
                        return Response({"status":True,"message":"liklyhood Probability Updated"})

                    else:
                        return Response({"status":False,"message":"Please provide symtom"})




            else:
                return Response({"status":False,"message":"Invalid action or name or probability"})




        except Exception as e:
            message = {'status':False}
            message.update(message=str(e))if settings.DEBUG else message.update(message='Internal server error')
            return Response(message,status=500)



class anlaysis_symtoms(APIView):
    def get(self,request):
        try:
            action = request.GET.get('action')
            versiondict = {"v1":"Chestpain Finding","v2":"Past Medical History","v3":"Cardiac Risk Factors","v4":"Physical Exam Findings","v5":"EKG","v6":"Labs","v7":"Chest X Ray","v8":"CT","v9":"Echocardiogram"}

            fetchQuestions = Questions.objects.filter(version_list = action ).values('id','version_list','question')
            for j in fetchQuestions:
                #fetch symtoms according to questions
                fetchsymtoms = symtoms.objects.filter(diseasesname__question__id = j['id']).values_list('name',flat=True).distinct()
                j['symtoms'] = fetchsymtoms


            versionobj = {"v1":"v2","v2":"v3","v3":"v4","v4":"v5","v5":"v6","v6":"v7","v7":"v8","v8":"null","v9":"null"}

            return Response({
                "status": True,
                "version":action,
                "nextversion":versionobj[action],
                "title":versiondict[action],
                "data":fetchQuestions


            })







        except Exception as e:
            message = {'status':False}
            message.update(message=str(e))if settings.DEBUG else message.update(message='Internal server error')
            return Response(message,status=500)


    def post(self, request):
        try:
            action = request.GET.get('action')
            data = request.data["current"]
            testsuggestion = list()
            symtomslist = list()

            for j in data:
                ## fetch symtoms
                fetchSymtoms = symtoms.objects.filter(name = j["symtoms"],diseasesname__question__id =j["id"]).values('probability',diseases_name = F('diseasesname__name'),prior = F('diseasesname__probability'))

                symtomslist.append(
                    {   "symtomsname":j["symtoms"],
                        "symtomslist":fetchSymtoms

                    }

                )


            Baysian_interference(symtomslist)
            finalprobability = calculate_probabilities(symtomslist)
            if request.data.get("previous",False) and action != "v1":
                previous = [request.data["previous"][-1]]
                previous.append({"symtomslist":finalprobability})
                finalprobability = marginalProbabilities(previous)

                # Now Suggest test if version = 4
                if action == "v4":
                    testsuggestion = test_suggestion(finalprobability)



            # if action != "v1":
            #     previous = request.data["previous"]
            #     previous.append({"symtomslist":finalprobability})

            #     finalprobability = calculate_probabilities(previous,"probability")




            versionobj = {"v1":"v2","v2":"v3","v3":"v4","v4":"v5","v5":"v6","v6":"v7","v7":"v8","v8":"null"}
            return Response({"version":versionobj[action],"status":True,"data":finalprobability,"testsuggestion":testsuggestion})







        except Exception as e:
            message = {'status':False}
            message.update(message=str(e))if settings.DEBUG else message.update(message='Internal server error')
            return Response(message,status=500)






class insert_prior_liklyhood(APIView):
    def post(self, request):
        try:
            action = request.GET.get('action')
            data = request.data
            bulklist = list()
            if action == "disease":
                for k in data:
                    fetchquestion = Questions.objects.get(version_list = k["version"],question = k["question"])

                    for l in k["disease"]:
                        bulklist.append(
                            diseases(name = l["disease"],question = fetchquestion,probability = l["prior"])
                        )







                diseases.objects.bulk_create(bulklist)
                return Response({"status":True,"message":"Insertion successfully"})

            else:
                for i in data:
                    for k in i["disease"]:
                        fetchspecificDiseases = diseases.objects.get(name = k["disease"],question__question = i["question"],question__version_list = i["version"])
                        bulklist.append(symtoms(name = i["question"],probability = k["liklyhood"],diseasesname = fetchspecificDiseases))




                symtoms.objects.bulk_create(bulklist)
                return Response({"status":False,"message":"Symtoms Adding successfully"})






        except Exception as e:
            message = {'status':False}
            message.update(message=str(e))if settings.DEBUG else message.update(message='Internal server error')
            return Response(message,status=500)




class updatetier(APIView):
    def get(self,request):
        v1 = Questions.objects.filter(version_list = "v1").values_list('question',flat=True)
        v2 = Questions.objects.filter(version_list = "v2").values_list('question',flat=True)
        v3 = Questions.objects.filter(version_list = "v3").values_list('question',flat=True)
        v4 = Questions.objects.filter(version_list = "v4").values_list('question',flat=True)
        v5 = Questions.objects.filter(version_list = "v5").values_list('question',flat=True)
        v6 = Questions.objects.filter(version_list = "v6").values_list('question',flat=True)


        print("v1",v1,len(v1))
        print("--------------------------------------------------------")
        print("v2",v2,len(v2))
        print("--------------------------------------------------------")
        print("v3",v3,len(v3))
        print("--------------------------------------------------------")
        print("v4",v4,len(v4))
        print("--------------------------------------------------------")
        print("v5",v5,len(v5))
        print("--------------------------------------------------------")
        print("v6",v6,len(v6))


        return Response({"status":True})



    def post(self,request):
        data = request.data["data"]
        version = request.data["updatedversion"]
        print("userinput",len(data))
        fetchdata = Questions.objects.filter(question__in = data)
        print("database",len(fetchdata))
        fetchdata.update(version_list = version)
        return Response({"status":True,"message":"Update Tier Successfully"})






class Ekgprediction(APIView):
    def post(self, request):
        try:
            samplefile = request.FILES.get('samplefile',False)
            if not samplefile:
                return Response({'status':False,'message':"samplefile in required in the numpy format"})

            diseaseList = ["Normal","Sinus tachy","ST depression","TWI","ST elevation","J point elevation/early repolarization"]
            sample = np.load(samplefile).reshape(5000,12)
            sample = np.array([sample], dtype=np.float32)
            # Provide input data
            input_details = model.get_input_details()
            model.set_tensor(input_details[0]['index'], sample)
            # Run inference
            model.invoke()
            # Get output predictions
            output_details = model.get_output_details()
            output_data = model.get_tensor(output_details[0]['index'])
            result = np.argmax(output_data)


            return Response({"status":True,"message":"Success","result":diseaseList[result]})

        except Exception as e:
            message = {'status':False}
            message.update(message=str(e))if settings.DEBUG else message.update(message='Internal server error')
            return Response(message,status=500)



# class Ekgprediction(APIView):
#     def post(self, request):
#         try:
#             samplefile = request.FILES.get('samplefile',False)
#             if not samplefile:
#                 return Response({'status':False,'message':"samplefile in required in the numpy format"})

#             diseaseList = ["Normal","Sinus tachy","ST depression","TWI","ST elevation"]
#             sample = np.load(samplefile).reshape(5000,12)
#             sample = np.array([sample])
#             Pr = model.predict(sample)
#             result = np.argmax(Pr)
#             return Response({"status":True,"message":"Success","result":diseaseList[result]})

#         except Exception as e:
#             message = {'status':False}
#             message.update(message=str(e))if settings.DEBUG else message.update(message='Internal server error')
#             return Response(message,status=500)

