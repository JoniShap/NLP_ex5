import wikipedia, spacy
nlp = spacy.load("en_core_web_sm")
page = wikipedia.page('Bradley Pitt').content
analyzed_page = nlp(page)


def find_proper_noun_sequences(doc):
    proper_nouns = []
    current_sequence = []

    for token in doc:
        if token.pos_ == "PROPN":
            current_sequence.append(token)
        else:
            if current_sequence:  # If we have a sequence
                if len(current_sequence) > 0:
                    proper_nouns.append(current_sequence)
                current_sequence = []

    # Don't forget the last sequence
    if current_sequence:
        proper_nouns.append(current_sequence)

    return proper_nouns