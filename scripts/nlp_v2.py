# -*- coding: utf-8 -*-
# neural_news
from textblob import TextBlob
import json
import sys

def analysis(text):
    blob      = TextBlob(text)
    sentences = blob.sentences
    result    = []
    for sentence in sentences:
        try:
            result.append({
                "text"     : str(sentence),
                "polarity" : str(sentence.polarity)
            })
        except:
            result.append({
                "text" : "nothing",
                "polarity" : "0"
            })
    print(json.dumps(result))
    sys.stdout.flush()

def main():
    article = sys.argv[1]
    analysis(article)

if __name__ == "__main__":
    main()
