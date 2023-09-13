from .models import Diagnosticinfo



def preprocess_questions(data):

    cardic = sum(j.priority for j in data if j.diseases_type == 'cardic')
    non_cardic = sum(j.priority for j in data if j.diseases_type != 'cardic')


    total_occurrences = cardic + non_cardic
    probability_of_cardic = cardic / total_occurrences * 100
    probability_of_uncardic = non_cardic / total_occurrences * 100
    return {
        # "totalcardic_symtoms":int(cardic/15),
        # "totalnoncardic_symtoms":int(non_cardic/5),
        "Cardic":int(probability_of_cardic),
        "Uncardic":int(probability_of_uncardic)

    }




def calculate_probabilities(symptom_list,keyname = "posterior"):
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


            average_posterior.append({
                "diseases_name":disease_name,
                "probability":round(posterior_sum[disease_name] / len(symptom_list),5)

            })

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
            marginal = round((Likelihood * Prior) + (1 - Likelihood) * (1 - Prior),3)

            ##posterior probability

            posterior = round((Likelihood * Prior) / marginal,3)
            j["posterior"] = posterior




#Marginal probabilities

def marginalProbabilities(data):
    finallist = list()
    for pre,latest in zip(data[0]["symtomslist"],data[1]["symtomslist"]):
        liklihood = latest["probability"]
        notliklyhood = 1 - liklihood
        prior = pre["probability"]
        notprior = 1 - prior



        # print("prior",prior)
        # print("liklihood",liklihood)
        # print("notliklyhood",notliklyhood)
        # print("notprior",notprior)


        x = (liklihood * prior) + (notliklyhood * notprior)
        # print("x",x)
        y = round(((liklihood * prior) / x) ,5)

        # print("marginal probability",y)
        # print("....x----------------")


        finallist.append({
            "diseases_name":latest["diseases_name"],
            "probability":y
        })




    return finallist



#Test suggestion






def test_suggestion(diseases):
    try:
        top_diseases = sorted(diseases, key=lambda x: x['probability'], reverse=True)[:3]
        top_disease_names = [disease['diseases_name'] for disease in top_diseases]
        fetch_disease_info = Diagnosticinfo.objects.filter(name__in=top_disease_names)

        test_suggestions_set = set()
        for k in fetch_disease_info:
            test_suggestions_set.update(k.diagnostic_test.split(','))

        return list(test_suggestions_set)

    except:
        return []