# data_processing.py
#
# Methods to process article data

import logging
from entity_analysis import analyzeEntitySentiment
from google.appengine.api import urlfetch

# Extract text from article urls
def processArticles(articles, startDate, aylienClient):
    results = []
    for article in articles[:5]:
        # Call alyien text API to extract text data and more from article url
        urlfetch.set_default_fetch_deadline(20)
        extract = aylienClient.Extract({'url': article['url'], 'best_image': True})
        logging.debug('Extracted text successfully')

        # Get text and titles fields from extracted
        text = extract['article']
        title = extract['title']
        fullText = title + '. ' + text

        # Perform entity analysis on text and title
        entities = analyzeEntitySentiment(fullText, startDate)

        results.append(entities)

    return results
