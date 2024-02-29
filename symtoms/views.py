from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serilizer import QuestionsSerilizer,FeedbackSerializer,AuthSerializer,LoginSerializer
import random
from .usable import *
from django.conf import settings
import pandas as pd
from pathlib import Path
import os
from django.db.models import F
import numpy as np
from rest_framework import status
from passlib.hash import django_pbkdf2_sha256 as handler
from .permission import Authorization
# from .loadingmodel import model,disease_model,tests_model
from django.utils.dateparse import parse_date


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


class dummydata(APIView):
    def get(self, request):
        try:
            action = request.GET.get("action", "v1")
            version = request.GET.get("version", "v1")
            if action == "disease":
                bulklist = list()
                file = pd.read_csv(BASE_DIR / "symtoms/files/tier_data/disease.csv")
                getQuestions = Questions.objects.filter(version_list=version)
                for i, j in zip(file["Diseases"], file["probability"]):
                    for k in getQuestions:
                        bulklist.append(diseases(name=i, question=k, probability=j))

                diseases.objects.bulk_create(bulklist)
                return Response(
                    {
                        "status": True,
                        "message": "Disease and Questions inserted successfully",
                    }
                )

            else:
                file = pd.read_csv(BASE_DIR / f"symtoms/files/tier_data/{action}.csv")
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
                        # fetch disease data
                        fetchspecificDiseases = diseases.objects.get(
                            name=totaldisease[i],
                            question__question=j,
                            question__version_list=version,
                        )

                        for k in range(len(specificdiseaseSymtoms)):
                            # chec if already exists

                            checkif = symtoms.objects.filter(
                                name=filterdata["Chest Pain"].iloc[k],
                                diseasesname=fetchspecificDiseases,
                            ).first()

                            if not checkif:
                                # print("if")
                                # print(filterdata["Chest Pain"].iloc[k])
                                # print(specificdiseaseSymtoms.iloc[k])
                                # print("----------------------------------------------------------------")
                                bulklist.append(
                                    symtoms(
                                        name=filterdata["Chest Pain"].iloc[k],
                                        probability=specificdiseaseSymtoms.iloc[k],
                                        diseasesname=fetchspecificDiseases,
                                    )
                                )

                            else:
                                # print("else")
                                # print(checkif.name)
                                # print(checkif.probability)
                                # print("----------------------------------------------------------------")

                                checkif.probability = specificdiseaseSymtoms.iloc[k]
                                checkif.save()

                # print("finallist",bulklist)
                if bulklist:
                    symtoms.objects.bulk_create(bulklist)

                return Response({"status": True, "message": "Insertion successfully"})

        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=500)


class manuplatedata(APIView):
    def get(self, request):
        try:
            allowaction = ["prior", "liklyhood"]
            action = request.GET.get("action")
            name = request.GET.get("name", False)
            Symtoms = request.GET.get("symtom", False)
            probability = request.GET.get("probability", False)

            if action in allowaction and name and probability:
                if action == "prior":
                    fetchPrior = diseases.objects.filter(name=name).update(
                        probability=probability
                    )
                    return Response(
                        {"status": True, "message": "Prior Probability Updated"}
                    )

                else:
                    if Symtoms:
                        fetchLikly = symtoms.objects.filter(
                            name=Symtoms, diseasesname__name=name
                        ).update(probability=probability)
                        return Response(
                            {"status": True, "message": "liklyhood Probability Updated"}
                        )

                    else:
                        return Response(
                            {"status": False, "message": "Please provide symtom"}
                        )

            else:
                return Response(
                    {
                        "status": False,
                        "message": "Invalid action or name or probability",
                    }
                )

        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=500)


class anlaysis_symtoms(APIView):
    def get(self, request):
        try:
            action = request.GET.get("action")
            versiondict = {
                "v1": "Chest Pain Finding",
                "v2": "Past Medical History",
                "v3": "Cardiac Risk Factors",
                "v4": "Physical Exam Findings",
                "v5": "EKG",
                "v6": "Labs",
                "v7": "Chest X Ray",
                "v8": "CT",
                "v9": "Echocardiogram",
            }

            fetchQuestions = Questions.objects.filter(version_list=action).values(
                "id", "version_list", "question"
            )
            for j in fetchQuestions:
                # fetch symtoms according to questions
                fetchsymtoms = (
                    symtoms.objects.filter(diseasesname__question__id=j["id"])
                    .values_list("name", flat=True)
                    .distinct()
                )
                j["symtoms"] = fetchsymtoms


            versionobj = {
                "v1": "v2",
                "v2": "v3",
                "v3": "v4",
                "v4": "v5",
                "v5": "v6",
                "v6": "v7",
                "v7": "v8",
                "v8": "null",
                "v9": "null",
            }
            #store all symtoms in a single array
            symtoms_list = list()
            for sym in fetchQuestions:
                symtoms_list += sym["symtoms"]

            return Response(
                {
                    "status": True,
                    "version": action,
                    "nextversion": versionobj[action],
                    "title": versiondict[action],
                    "data": fetchQuestions,
                    "symtoms":symtoms_list
                }
            )

        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=500)

    def post(self, request):
        try:
            action = request.GET.get("action")
            data = request.data["current"]
            testsuggestion = []
            previous_suggestion = request.data.get("previous_suggestion", False)
            symtomslist = list()
            for j in data:
                ## fetch symtoms
                fetchSymtoms = symtoms.objects.filter(
                    name=j["symtoms"], diseasesname__question__id=j["id"]
                ).values(
                    "probability",
                    diseases_name=F("diseasesname__name"),
                    prior=F("diseasesname__probability"),
                )
                symtomslist.append(
                    {"symtomsname": j["symtoms"], "symtomslist": fetchSymtoms}
                )
            Baysian_interference(symtomslist)
            finalprobability = calculate_probabilities(symtomslist)
            if action == "v1" or action == "v2" or action == "v3" or action == "v4":
                testsuggestion = test_suggestion_average(data)

            if (
                request.data.get("previous", False)
                and action != "v1"
                and previous_suggestion
            ):
                previous = [request.data["previous"][-1]]
                previous.append({"symtomslist": finalprobability})
                finalprobability = marginalProbabilities(previous)

                if action == "v1" or action == "v2" or action == "v3" or action == "v4":
                    testsuggestion = test_suggestion_marginal_probabilities(
                    previous_suggestion, testsuggestion)

            versionobj = {
                "v1": "v2",
                "v2": "v3",
                "v3": "v4",
                "v4": "v5",
                "v5": "v6",
                "v6": "v7",
                "v7": "v8",
                "v8": "null",
            }

            ##sort the disease and test recommendations array
            finalprobability = sort_discending_order(finalprobability)
            testsuggestion = sort_discending_order(testsuggestion)
            return Response(
                {
                    "status": True,
                    "version": versionobj[action],
                    "data": finalprobability,
                    "testsuggestion": testsuggestion,
                }
            )

        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=500)

class Both_symtoms(APIView):
    def post(self,request):
        try:

            action = request.GET.get("action")
            data = request.data["current"]
            all_symtoms = request.data.get("all_symtoms")
            beta_model_response = {}
            testsuggestion = []
            previous_suggestion = request.data.get("previous_suggestion", False)
            symtomslist = list()
            for j in data:
                ## fetch symtoms
                fetchSymtoms = symtoms.objects.filter(
                    name=j["symtoms"], diseasesname__question__id=j["id"]
                ).values(
                    "probability",
                    diseases_name=F("diseasesname__name"),
                    prior=F("diseasesname__probability"),
                )
                symtomslist.append(
                    {"symtomsname": j["symtoms"], "symtomslist": fetchSymtoms}
                )
            Baysian_interference(symtomslist)
            finalprobability = calculate_probabilities(symtomslist)
            if action == "v1" or action == "v2" or action == "v3" or action == "v4":
                testsuggestion = test_suggestion_average(data)

            if (
                request.data.get("previous", False)
                and action != "v1"
                and previous_suggestion
            ):
                previous = [request.data["previous"][-1]]
                previous.append({"symtomslist": finalprobability})
                finalprobability = marginalProbabilities(previous)

                if action == "v1" or action == "v2" or action == "v3" or action == "v4":
                    testsuggestion = test_suggestion_marginal_probabilities(
                    previous_suggestion, testsuggestion)

            versionobj = {
                "v1": "v2",
                "v2": "v3",
                "v3": "v4",
                "v4": "v5",
                "v5": "v6",
                "v6": "v7",
                "v7": "v8",
                "v8": "null",
            }

            ##sort the disease and test recommendations array
            finalprobability = sort_discending_order(finalprobability)
            testsuggestion = sort_discending_order(testsuggestion)
            ##merge the beta model response
            if all_symtoms:
                # url = f"{request.META['wsgi.url_scheme']}://{request.META['HTTP_HOST']}/ekg/beta/anlaysis_symtoms/?action=v1"
                # beta_model_response = beta_model_daignosis(all_symtoms,url)

                beta_model_response = beta_model_daignosis(all_symtoms)

            return Response(
                {   "status":True,
                    "live":{
                    "status": True,
                    "version": versionobj[action],
                    "data": finalprobability,
                    "testsuggestion": testsuggestion,
                },
                "beta":beta_model_response
                }

            )

        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=500)

class Beta_anlaysis_symtoms(APIView):
    def get(self, request):
        try:
            action = request.GET.get("action")
            versiondict = {
                "v1": "Tier 1",
                "v2": "Tier 2",
                "v3":"null"
            }

            fetchQuestions = Questions.objects.using("beta").filter(version_list=action).values(
                "id", "version_list", "question"
            )
            for j in fetchQuestions:
                # fetch symtoms according to questions
                fetchsymtoms = (
                    symtoms.objects.using("beta").filter(diseasesname__question__id=j["id"])
                    .values_list("name", flat=True)
                    .distinct()
                )
                j["symtoms"] = fetchsymtoms

            versionobj = {
                "v1": "v2",
                "v2": False

            }
            #store all symtoms in a single array
            symtoms_list = list()
            for sym in fetchQuestions:
                symtoms_list += sym["symtoms"]

            return Response(
                {
                    "status": True,
                    "version": action,
                    "nextversion": versionobj[action],
                    "title": versiondict[action],
                    "data": fetchQuestions,
                    "symtoms":symtoms_list
                }
            )

        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=500)

    def post(self, request):
        symtoms_data = request.data["data"]
        action = request.GET["action"]
        #disase recommadations
        disease_data = pd.read_csv('models/beta/disease_sheet.csv')
        diseases = disease_data['Diseases']
        disease_symptoms = disease_data.drop(['Diseases'], axis=1)
        disease_probability = recommend_disease(symtoms_data,disease_symptoms,disease_model)

        #tests recommendations
        tests_data = pd.read_csv('models/beta/tests_sheet.csv')
        tests = tests_data['Tests']
        tests_symptoms = tests_data.drop(['Tests'], axis=1)
        test_recommendation = recommend_test(symtoms_data,tests_symptoms,tests_model)

        versionobj = {"v1":"v2","v2":"null"}
        ##sort the disease and test recommendations array
        disease_probability = sort_discending_order(disease_probability)
        test_recommendation = sort_discending_order(test_recommendation)
        response_data = {
            "status":True,
            "version": versionobj[action],
            "data":disease_probability,
            "testsuggestion":test_recommendation
        }
        return Response(response_data)


class anlaysis_prescription(APIView):
    def post(self, request):
        try:
            prescription = request.data.get("prescription")
            symtoms = request.data.get("symtoms")
            if not prescription:
                return Response({"status": False, "message": "Prescription is missing"}, status=status.HTTP_400_BAD_REQUEST)
            if not symtoms:
                return Response({"status": False, "message": "Symptoms are missing"}, status=status.HTTP_400_BAD_REQUEST)

            suggested_symtoms = suggest_sytoms(prescription,symtoms)
            return Response({"status":True,"data":suggested_symtoms})

        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class insert_prior_liklyhood(APIView):
    def post(self, request):
        try:
            action = request.GET.get("action")
            data = request.data
            bulklist = list()
            if action == "disease":
                for k in data:
                    fetchquestion = Questions.objects.get(
                        version_list=k["version"], question=k["question"]
                    )

                    for l in k["disease"]:
                        bulklist.append(
                            diseases(
                                name=l["disease"],
                                question=fetchquestion,
                                probability=l["prior"],
                            )
                        )

                diseases.objects.bulk_create(bulklist)
                return Response({"status": True, "message": "Insertion successfully"})

            else:
                for i in data:
                    for k in i["disease"]:
                        fetchspecificDiseases = diseases.objects.get(
                            name=k["disease"],
                            question__question=i["question"],
                            question__version_list=i["version"],
                        )
                        bulklist.append(
                            symtoms(
                                name=i["question"],
                                probability=k["liklyhood"],
                                diseasesname=fetchspecificDiseases,
                            )
                        )

                symtoms.objects.bulk_create(bulklist)
                return Response(
                    {"status": False, "message": "Symtoms Adding successfully"}
                )

        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=500)


class updatetier(APIView):
    def get(self, request):
        v1 = Questions.objects.filter(version_list="v1").values_list(
            "question", flat=True
        )
        v2 = Questions.objects.filter(version_list="v2").values_list(
            "question", flat=True
        )
        v3 = Questions.objects.filter(version_list="v3").values_list(
            "question", flat=True
        )
        v4 = Questions.objects.filter(version_list="v4").values_list(
            "question", flat=True
        )
        v5 = Questions.objects.filter(version_list="v5").values_list(
            "question", flat=True
        )
        v6 = Questions.objects.filter(version_list="v6").values_list(
            "question", flat=True
        )

        print("v1", v1, len(v1))
        print("--------------------------------------------------------")
        print("v2", v2, len(v2))
        print("--------------------------------------------------------")
        print("v3", v3, len(v3))
        print("--------------------------------------------------------")
        print("v4", v4, len(v4))
        print("--------------------------------------------------------")
        print("v5", v5, len(v5))
        print("--------------------------------------------------------")
        print("v6", v6, len(v6))

        return Response({"status": True})

    def post(self, request):
        data = request.data["data"]
        version = request.data["updatedversion"]
        print("userinput", len(data))
        fetchdata = Questions.objects.filter(question__in=data)
        print("database", len(fetchdata))
        fetchdata.update(version_list=version)
        return Response({"status": True, "message": "Update Tier Successfully"})


class Ekgprediction(APIView):
    def post(self, request):
        try:
            samplefile = request.FILES.get("samplefile", False)
            if not samplefile:
                return Response(
                    {
                        "status": False,
                        "message": "samplefile in required in the numpy format",
                    }
                )

            diseaseList = [
                "Normal",
                "Sinus tachy",
                "ST depression",
                "TWI",
                "ST elevation",
                "J point elevation",
                "NST's"
            ]
            sample = np.load(samplefile).reshape(5000, 12)
            sample = np.array([sample], dtype=np.float32)
            # Provide input data
            input_details = model.get_input_details()
            model.set_tensor(input_details[0]["index"], sample)
            # Run inference
            model.invoke()
            # Get output predictions
            output_details = model.get_output_details()
            output_data = model.get_tensor(output_details[0]["index"])
            result = np.argmax(output_data)

            return Response(
                {"status": True, "message": "Success", "result": diseaseList[result]}
            )

        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=500)

class Recordfeedback(APIView):
    permission_classes = [Authorization]

    def get_permissions(self, *args, **kwargs):
        if self.request.method in ["GET"]:
            return [Authorization()]
        else:
            return []

    def get(self,request):
        try:
            filters = {}
            correct_status = request.GET.get('correct_status', None)
            difficult_level = request.GET.get('difficult_level', None)
            prediction_model = request.GET.get('prediction_model', None)
            start_date_param = request.GET.get('start_date', None)
            end_date_param = request.GET.get('end_date', None)

            # Add filters to the dictionary only if they are provided
            if correct_status:
                filters['correct_status'] = correct_status
            if difficult_level:
                filters['difficult_level'] = difficult_level
            if prediction_model:
                filters['prediction_model'] = prediction_model
            if start_date_param and end_date_param:
                start_date = parse_date(start_date_param)
                end_date = parse_date(end_date_param)
                end_date += timezone.timedelta(days=1)
                filters['created_at__range'] = (start_date,end_date)

            # Build the queryset based on the provided filters
            queryset = Feedback.objects.filter(**filters)
            # Serialize the filtered queryset
            serializer_feedback = FeedbackSerializer(queryset, many=True)

            #count the total number of correct results
            model_right = model_statistics(serializer_feedback.data,"correct_status","Right")

            #count the total number of Partially correct results
            model_partially_right = model_statistics(serializer_feedback.data,"correct_status","Partially Right")

            #count the total number of wrong results
            model_wrong = model_statistics(serializer_feedback.data,"correct_status","Wrong")


            return Response({"status": True, "data": serializer_feedback.data,"right":model_right,"partially_right":model_partially_right,"wrong":model_wrong})
        except Exception as e:
            return Response({'status':False,'errors':str(e)},status=403)

    def post(self,request):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status":True,"data":serializer.data}, status=status.HTTP_201_CREATED)

        error = execptionhandler(serializer)
        return Response({"status":False,"error":error}, status=status.HTTP_400_BAD_REQUEST)



class Registration(APIView):
    def post(self, request):
        auth_serializer = AuthSerializer(data=request.data)
        if auth_serializer.is_valid():
            auth_serializer.save()
            return Response({"status":True,"data":auth_serializer.data}, status=status.HTTP_201_CREATED)

        error = execptionhandler(auth_serializer)
        return Response({"status":False,"error":error}, status=status.HTTP_400_BAD_REQUEST)

class Login(APIView):
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if not serializer.is_valid():
                error = execptionhandler(serializer)
                return Response({'status': False, 'message': error}, status=422)

            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            Admin_obj = Auth.objects.filter(email=email).first()
            if not Admin_obj or not handler.verify(password, Admin_obj.password):
                return Response({'status': False, 'message': 'Invalid Credential'}, status=403)

            if not Admin_obj.is_active:
                return Response({'status': False, 'message': 'Your Account is not active'}, status=403)

            jwtkey = "=snzbxs@shak0888"
            token_obj = generatedToken(Admin_obj, jwtkey, 120)
            if not token_obj['status']:
                return Response(token_obj, status=500)

            return Response({
                'status': True,
                'message': 'Login Successfully',
                'token': token_obj['token'],
                'data': token_obj['payload']
            }, status=200)

        except Exception as e:
            return Response({'status':False,'errors':str(e)},status=403)


class UpdateProbablities(APIView):
    """
    Update Probabilty in Database, a/c symptoms and its disease 

    The class has an POST method API which is taking a csv file in (form-data)
    convert the csv file in the List and Object Architecture so easily readable
        i.e 
            json_data = {
                "Gripping": {               # symptoms
                    "Pulmonary": 0.05,      # disease with probability
                    "Eso rupture": 0.6
                },
                "Ripping": {               # symptoms
                    "Pulmonary": 0.5,      # disease with probability
                    "Eso rupture": 0.8
                }
            }

    Update the Probability in DATABASE a/c to symptoms and its disease

    """
    def post(self, request):

        try:
            csv_file = request.FILES.get('file', None)  # Assuming 'file' is the key for the uploaded CSV file
            
            if not csv_file:
                return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
       
            if not csv_file.name.endswith('.csv'):
                return Response({'error': 'Not a CSV file'}, status=status.HTTP_400_BAD_REQUEST)


            df = pd.read_csv(csv_file)
            json_data = {}

            for index, row in df.iterrows():
                symptoms = row['symptoms']  # Get the symptom name
                symptom_data = {}
                # Iterate over each disease column in the row
                for disease in df.columns[1:]:
                    probability = row[disease]  # Get the probability value
                    symptom_data[disease] = probability  # Add disease probability to symptom data
                    
                # Add symptom data to the main JSON data dictionary
                json_data[symptoms] = symptom_data
            
            # print(json.dumps(json_data, indent=2))
            
            # track not_found data in db AND multiple_symptms_and_disease
            not_found= []
            multiple_objects= []

            for symptom, diseases_data in json_data.items():

                for disease, probability in diseases_data.items():
                    obj= {
                            "symptom_name in csv": symptom,
                            "dieases name in csv": disease,
                            "probability in csv": probability
                        }
                    
                    print(f"symptom_name in csv: {symptom}")
                    print(f"dieases name in csv: {disease}")

                    symptom_filter = symtoms.objects.filter(
                        name__startswith = symptom,
                        diseasesname__name= disease
                        )
                    print("LENGTH IS ",len(symptom_filter))
                    
                    if len(symptom_filter) >=2 :
                        multiple_objects.append(obj)
                        continue
                    
                    symptom_obj= symptom_filter.first()
                    if symptom_filter and symptom_obj is not None:
                        print("symptom_obj name in DB: ",symptom_obj)
                        print("symptom_obj probability in DB: ",symptom_obj.probability)
                        print(f"probability in csv: {probability}")

                        if probability == symptom_obj.probability:
                            print("********** PROBABLITY ARE SAME **********")
                        else :
                            symptom_obj.probability = probability
                            symptom_obj.save()
                            print("########### PROBABLITY ARE Different #######################################################")

                    else:
                        not_found.append(obj)

                    print("\n\n")
            
            return Response({
                "status":True,
                "message": "check console",
                "fetching_multiple_objects_in_db": multiple_objects,
                "not_found_in_db_data": not_found
            }, status=status.HTTP_200_OK
            )

        except Exception as swr:
            return Response({
                "status": False,
                "message": f"Somethong wents wrong, General Exceaption {swr}"
            }, status= status.HTTP_400_BAD_REQUEST
            )


class UpdateOurCSVs(APIView):
    """
    This API is reponsible to update our csv files in our project directory 
        i.e.    - updated_csv/beta    ( update_physical_finding.csv )
                - updated_csv/live
    
    """
    def get(self, request):
        for_db= request.GET.get("db", None)

        if not for_db:
            for_db = 'default'
            directory_path = "updated_csv/default/"

        if for_db:
            directory_path = f"updated_csv/{for_db}/"

        csv_files = [file for file in os.listdir(directory_path) if file.endswith('.csv')]

        symtoms_disease_len= [] # check having more than 11 record of same symotoms
        name_conflict_symptoms_query= []  # check having more than 1 symptoms name in same disease
        symptoms_not_found = []  # check those symptoms not found in DB but in csv
        
        # Specify the database to use based on 'for_db' parameter
        db_alias = 'beta' if for_db == 'beta' else 'default'

        for csv_file in csv_files:
            csv_file_path = os.path.join(directory_path, csv_file)
            df = pd.read_csv(csv_file_path)

            for index , row in df.iterrows():
                csv_symptoms = row['Chest Pain']
                print(csv_symptoms)

                # check_symptoms = symtoms.objects.filter(name__startswith = csv_symptoms)
                check_symptoms = symtoms.objects.using(db_alias).filter(name__startswith=csv_symptoms)

                if len(check_symptoms) > 11:
                    symtoms_disease_len.append(csv_symptoms)

                for disease , probability in row[2:].items():
                    obj = {
                        "csv_symptoms": csv_symptoms,
                        "disease": disease,
                        "probability": probability
                    }

                    print(f"csv_symptoms = {csv_symptoms} disease is =  {disease} and probablity is {probability}"  )

                    fetch_default_symptom = symtoms.objects.using(db_alias).filter(
                        name__startswith=csv_symptoms,
                        diseasesname__name=disease
                    )
                    if len(fetch_default_symptom) > 1:
                        name_conflict_symptoms_query.append(obj)

                    fetch_symptom = fetch_default_symptom.first()
                    if fetch_symptom:
                        print( f"database symptoms = {fetch_symptom.name}, Disease = {fetch_symptom.diseasesname}, probab= {fetch_symptom.probability}")

                        # check the probability if different in csv and DB
                        if probability != fetch_symptom.probability:
                            print("________________________   DIFFERENT PROBABILITY ________________")
                            # update probablity in dataframe for csv 
                            df.at[index, disease] = fetch_symptom.probability
                    
                        print("\n\n")
                    
                    else :
                        symptoms_not_found.append(obj)
            
            df.to_csv(f"{directory_path}/updated__{csv_file}", index=False)

        
        return Response({
            "status": True,
            "message": "csv Updated Successfully",
            "more than 11 symptoms in DB": symtoms_disease_len,
            "more than 1 symptoms with same disease in DB": name_conflict_symptoms_query,
            "symptoms_not_found in db": symptoms_not_found
            }, status= 200)




