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
        return doc


    except wikipedia.exceptions.WikipediaException as e:
        print(f"Error fetching page {title}: {e}")
        return []


def find_proper_noun_heads(doc):
    lst = []
    for token in doc:
        if token.pos_ == "PROPN" and token.dep_ != "compound":
            lst.append(token)
    return lst

def get_complete_proper_noun(head):
    lst = []
    for token in head.children:
        if token.dep_ == "compound":
            lst.append(token)
    return lst + [head]


def extract_relations_dependency(doc):
    triplets = []

    # Process sentence by sentence
    for sent in doc.sents:
        # Find all proper noun heads in this sentence
        heads = find_proper_noun_heads(sent)

        # Look at each pair of heads
        for h1 in heads:
            for h2 in heads:
                if h1 != h2:
                    # Get the complete proper nouns
                    noun1 = get_complete_proper_noun(h1)
                    noun2 = get_complete_proper_noun(h2)

                    # Check condition #1: same head with nsubj and dobj
                    if (h1.head == h2.head and
                            h1.dep_ == "nsubj" and
                            h2.dep_ == "dobj"):
                        # The relation is the shared head
                        relation = h1.head
                        triplets.append((
                            " ".join(t.text for t in noun1),
                            relation.text,
                            " ".join(t.text for t in noun2)
                        ))

                    # Check condition #2: nsubj + prep + pobj pattern
                    elif (h1.dep_ == "nsubj" and
                          h2.dep_ == "pobj" and
                          h2.head.dep_ == "prep" and
                          h2.head.head == h1.head):
                        # The relation is head + preposition
                        relation = f"{h1.head.text} {h2.head.text}"
                        triplets.append((
                            " ".join(t.text for t in noun1),
                            relation,
                            " ".join(t.text for t in noun2)
                        ))

    return triplets


import random
from collections import defaultdict


def evaluate_extractors(titles):
    """
    Evaluate both extractors on given Wikipedia pages

    Args:
        titles (list): List of Wikipedia page titles to analyze
    """
    # Dictionary to store results for each extractor
    results = defaultdict(dict)

    # Process each page with both extractors
    for title in titles:
        try:
            # Get page content
            page = wikipedia.page(title).content
            doc = nlp(page)

            # Get results from both extractors
            pos_triplets = extract_relations(doc)  # POS-based extractor
            dep_triplets = extract_relations_dependency(doc)  # Dependency-based extractor

            # Store total counts
            results[title]['pos_count'] = len(pos_triplets)
            results[title]['dep_count'] = len(dep_triplets)

            # Get random samples for manual verification
            if pos_triplets:
                results[title]['pos_sample'] = random.sample(
                    pos_triplets,
                    min(5, len(pos_triplets))
                )
            if dep_triplets:
                results[title]['dep_sample'] = random.sample(
                    dep_triplets,
                    min(5, len(dep_triplets))
                )

        except wikipedia.exceptions.WikipediaException as e:
            print(f"Error processing {title}: {e}")
            continue

    return results




# Print results in a readable format
def print_evaluation_results(results):
    print("\nEVALUATION RESULTS")
    print("=" * 50)

    for title in results:
        print(f"\n{title}:")
        print("-" * 30)
        print(f"POS-based extractor found: {results[title]['pos_count']} triplets")
        print(f"Dependency-based extractor found: {results[title]['dep_count']} triplets")

        print("\nPOS-based samples for manual verification:")
        for triplet in results[title].get('pos_sample', []):
            print(f"- Subject: {triplet[0]}")
            print(f"  Relation: {triplet[1]}")
            print(f"  Object: {triplet[2]}")
            print(f"  Valid? (Y/N): ")  # For manual input

        print("\nDependency-based samples for manual verification:")
        for triplet in results[title].get('dep_sample', []):
            print(f"- Subject: {triplet[0]}")
            print(f"  Relation: {triplet[1]}")
            print(f"  Object: {triplet[2]}")
            print(f"  Valid? (Y/N): ")  # For manual input







# Example usage
nlp = spacy.load("en_core_web_sm")
# title = "Bradley Pitt"
# analyzed_doc = extract_from_wikipedia(title)
# triplets_pos = extract_relations(analyzed_doc)
#
# triplets_trees = extract_relations_dependency(analyzed_doc)

# Run evaluation
titles = [
    "Donald Trump",
    "Ruth Bader Ginsburg",
    "J. K. Rowling"
]

results = evaluate_extractors(titles)

# Run and print results
print_evaluation_results(results)

