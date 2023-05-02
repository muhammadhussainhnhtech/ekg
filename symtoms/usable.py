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