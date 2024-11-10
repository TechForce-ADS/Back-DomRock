from textblob import TextBlob

def get_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0.1:
        return 'positivo'
    elif analysis.sentiment.polarity < -0.1:
        return 'negativo'
    return 'neutro'
