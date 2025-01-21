import wikipedia, spacy




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


def find_proper_noun_pairs(doc):
    pairs = []
    proper_nouns = find_proper_noun_sequences(doc)

    # Look at each possible pair of proper noun sequences
    for i in range(len(proper_nouns)):
        for j in range(i + 1, len(proper_nouns)):
            first = proper_nouns[i]
            second = proper_nouns[j]

            # Get the span between these sequences
            start_idx = first[-1].i + 1  # End of first sequence
            end_idx = second[0].i  # Start of second sequence

            if start_idx >= end_idx:
                continue

            between_tokens = doc[start_idx:end_idx]

            # Check if there's at least one verb and no punctuation
            has_verb = False
            has_punct = False

            for token in between_tokens:
                if token.pos_ == "VERB":
                    has_verb = True
                if token.pos_ == "PUNCT":
                    has_punct = True
                    break

            if has_verb and not has_punct:
                pairs.append((first, between_tokens, second))

    return pairs


def extract_relations(doc):
    triplets = []
    pairs = find_proper_noun_pairs(doc)

    for first, between, second in pairs:
        # Convert first proper noun sequence to string
        subject = " ".join([token.text for token in first])

        # Convert second proper noun sequence to string
        obj = " ".join([token.text for token in second])

        # Extract only verbs and prepositions from between tokens
        relation = []
        for token in between:
            if token.pos_ in ["VERB", "ADP"]:  # VERB or preposition
                relation.append(token.text)

        relation = " ".join(relation)

        if relation:  # Only add if we found a relation
            triplets.append((subject, relation, obj))

    return triplets


def extract_from_wikipedia(title):
    # Get Wikipedia content
    try:
        page = wikipedia.page(title).content
        doc = nlp(page)

        # Process sentence by sentence to keep things manageable
        triplets = extract_relations(doc)
        return triplets

    except wikipedia.exceptions.WikipediaException as e:
        print(f"Error fetching page {title}: {e}")
        return []


def find_poroper_nouns_heads(doc):
    lst = []
    for token in doc:
        if token.pos_ == "PROPN" and token.dep_ != "compound":
            lst.append(token.head)
    return lst
def get_complete_proper_nouns(head):
    lst = []
    for token in head.children:
        if token.dep_ == "compound":
            lst.append(token)
    return lst + [head]





# Example usage
nlp = spacy.load("en_core_web_sm")
title = "Bradley Pitt"
triplets_pos = extract_from_wikipedia(title)
