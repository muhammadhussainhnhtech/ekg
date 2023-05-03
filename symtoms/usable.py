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



def calculate_probabilities(data):
    if data:
        probalilityobj = list(data[0]["symtomslist"])
        for i in range(1,len(data)):
            for j in range(len(data[i]["symtomslist"])):
                valueSum = round(probalilityobj[j]["probability"] + data[i]["symtomslist"][j]["probability"],2)
                probalilityobj[j]["probability"]  = valueSum
            
        return probalilityobj

    else:
        return False