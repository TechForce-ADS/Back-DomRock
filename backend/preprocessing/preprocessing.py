import re
import nltk
from nltk.corpus import wordnet

nltk.download('wordnet')

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\W+', ' ', text)
    return text

def expand_query(query, limit=5):
    synonyms = set()
    for syn in wordnet.synsets(query):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return list(synonyms)[:limit] if synonyms else [query]
