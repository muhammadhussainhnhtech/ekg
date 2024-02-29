from .models import Diagnosticinfo
import pandas as pd
from pathlib import Path
# from fuzzywuzzy import process
import re
import requests
import json
from .loadingmodel import disease_model,tests_model
from django.utils import timezone
from datetime import timedelta
import jwt

BASE_DIR = Path(__file__).resolve().parent.parent


def preprocess_questions(data):
    cardic = sum(j.priority for j in data if j.diseases_type == "cardic")
    non_cardic = sum(j.priority for j in data if j.diseases_type != "cardic")
    total_occurrences = cardic + non_cardic
    probability_of_cardic = cardic / total_occurrences * 100
    probability_of_uncardic = non_cardic / total_occurrences * 100
    return {
        "Cardic": int(probability_of_cardic),
        "Uncardic": int(probability_of_uncardic),
    }


def calculate_probabilities(symptom_list, keyname="posterior"):
    if symptom_list:
        posterior_sum = {}
        for symptom in symptom_list:
            for disease in symptom["symtomslist"]:
                disease_name = disease["diseases_name"]
                posterior = disease[keyname]
                if disease_name not in posterior_sum:
                    posterior_sum[disease_name] = posterior

                else:
                    posterior_sum[disease_name] += posterior
        ##calculate the average
        average_posterior = list()
        for disease_name in posterior_sum:
            average_posterior.append(
                {
                    "diseases_name": disease_name,
                    "probability": round(
                        posterior_sum[disease_name] / len(symptom_list), 5
                    ),
                }
            )
        return average_posterior

    else:
        return False


##calculate the posterior probabilities using Baysian Interference
def Baysian_interference(payload):
    for i in payload:
        for j in i["symtomslist"]:
            Likelihood = j["probability"]
            Prior = j["prior"]
            ##marginal probability
            marginal = round((Likelihood * Prior) + (1 - Likelihood) * (1 - Prior), 3)
            ##posterior probability
            posterior = round((Likelihood * Prior) / marginal, 3)
            j["posterior"] = posterior


# Marginal probabilities
def marginalProbabilities(data):
    finallist = list()
    for pre, latest in zip(data[0]["symtomslist"], data[1]["symtomslist"]):
        liklihood = latest["probability"]
        notliklyhood = 1 - liklihood
        prior = pre["probability"]
        notprior = 1 - prior
        x = (liklihood * prior) + (notliklyhood * notprior)
        y = round(((liklihood * prior) / x), 5)
        finallist.append({"diseases_name": latest["diseases_name"], "probability": y})

    return finallist


def test_suggestion_average(data):
    read_file = pd.read_csv(
        f"{BASE_DIR}/symtoms/files/test_suggestion/symtoms_probability_v3.csv", index_col="name"
    )
    # Extract the list of symptom names from input_data
    symptom_names = [entry["symtoms"] for entry in data]
    # Filter the DataFrame rows based on symptom names
    filtered_data = read_file.loc[symptom_names]
    column_averages = filtered_data.mean().to_dict()
    # Round the average values to two decimal places
    rounded_column_averages = {
        key: round(value, 2) for key, value in column_averages.items()
    }
    # Convert the dictionary to a list of dictionaries
    suggestions = [
        {"test_name": key, "probability": value/100}
        for key, value in rounded_column_averages.items()
    ]
    return suggestions


def test_suggestion_marginal_probabilities(pre_data, latest_data):
    finallist = list()
    for pre, latest in zip(pre_data, latest_data):
        liklihood = latest["probability"]
        notliklyhood = 1 - liklihood
        prior = pre["probability"]
        notprior = 1 - prior
        x = (liklihood * prior) + (notliklyhood * notprior)
        y = round(((liklihood * prior) / x), 5)
        finallist.append({"test_name": latest["test_name"], "probability": y})


    return finallist


def suggest_sytoms(prescription:str,symtoms:list)->list:
    """Suggests symptoms that may be relevant to a given prescription"""
    # Split the query into parts
    query_tokens = re.split(r'[ ,]', prescription)
    matching_keywords = []
    common_words = [
    "a", "about", "above", "after", "again", "against", "ain't", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot",
    "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few",
    "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's",
    "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've",
    "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves",
    "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they",
    "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very",
    "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you",
    "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
    ]
    for token in query_tokens:
        # Filter out common words
        if token.lower() not in common_words:
            best_match = process.extractOne(token, symtoms)
            if best_match[1] >= 85:
                matching_keywords.append(best_match[0])

    return matching_keywords


def recommend_disease(user_input, disease_symptoms, disease_model):
    """Updated recommend_disease function to include probability scores"""
    user_symptoms = {symptom: 0.0 for symptom in disease_symptoms.columns}
    for item in user_input:
        symptom = item.get('symtoms')
        if symptom in user_symptoms:
            user_symptoms[symptom] = 1.0  # You can set the probability as needed

    user_symptom_probabilities = [user_symptoms[symptom] for symptom in disease_symptoms.columns]
    disease_probs = disease_model.predict_proba([user_symptom_probabilities])[0]
    # Create a list of dictionaries for the JSON response
    response = [
        {"diseases_name": disease, "probability": prob}
        for disease, prob in zip(disease_model.classes_, disease_probs)
    ]

    return response


def recommend_test(user_input, tests_symptoms, tests_model):
    user_symptoms = {symptom: 0.0 for symptom in tests_symptoms.columns}

    # Extract symptoms from the input format
    for item in user_input:
        symptom = item.get('symtoms')
        if symptom in user_symptoms:
            user_symptoms[symptom] = 1.0  # You can set the probability as needed

    user_symptom_probabilities = [user_symptoms[symptom] for symptom in tests_symptoms.columns]
    tests_probs = tests_model.predict_proba([user_symptom_probabilities])[0]

    # Get the test with the highest probability
    max_prob_idx = tests_probs.argmax()
    recommend_test = tests_model.classes_[max_prob_idx]

    # Create a list of dictionaries for the JSON response
    response = [
        {"test_name": tests, "probability": round(prob,3)}
        for tests, prob in zip(tests_model.classes_, tests_probs)
    ]
    return response



def sort_discending_order(diseases):
    sorted_diseases = sorted(diseases, key=lambda x: x["probability"], reverse=True)
    return sorted_diseases

def execptionhandler(val):
        if 'error' in val.errors:
            error = val.errors["error"][0]
        else:
            key = next(iter(val.errors))
            error = key + ", " + val.errors[key][0]

        return error

def generatedToken(fetchuser, jwt_key, totaldays):
    try:
        access_token_payload = {
            "id": str(fetchuser.id),
            "iat": timezone.now(),
            "exp": timezone.now() + timedelta(days=totaldays),
        }
        userpayload = {
            "id": str(fetchuser.id),
            "email": fetchuser.email,
            "fname": fetchuser.fname,
            "lname": fetchuser.lname,
        }
        access_token = jwt.encode(access_token_payload, jwt_key, algorithm="HS256")
        return {"status": True, "token": access_token, "payload": userpayload}

    except Exception as e:
        return {
            "status": False,
            "message": "Something went wrong in token creation",
            "details": str(e),
        }

def model_statistics(feedbacks,key,critarea):
    prediction_model = {
        "Beta":0,
        "Live":0
    }
    for feedback in feedbacks:
        if feedback["prediction_model"] == "Beta" and  feedback[key] == critarea:
            prediction_model["Beta"] +=1

        elif feedback["prediction_model"] == "Live" and  feedback[key] == critarea:
            prediction_model["Live"] +=1

    total_predictions = prediction_model["Beta"] +  prediction_model["Live"]
    if total_predictions > 0:
        prediction_model["Beta"] = round(prediction_model["Beta"]/total_predictions,2)
        prediction_model["Live"] = round(prediction_model["Live"]/total_predictions,2)
    return prediction_model


# def beta_model_daignosis(data,url):
#     payload = json.dumps({
#     "data": data
#     })
#     headers = {
#     'Content-Type': 'application/json'
#     }
#     response = requests.request("POST", url, headers=headers, data=payload)
#     return response.json()

def beta_model_daignosis(symtoms_data):
    action = "v1"
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
    return response_data