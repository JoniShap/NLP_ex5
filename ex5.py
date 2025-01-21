import wikipedia, spacy
nlp = spacy.load("en_core_web_sm")
page = wikipedia.page('Bradley Pitt').content
analyzed_page = nlp(page)


