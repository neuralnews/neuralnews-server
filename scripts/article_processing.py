# data_processing.py
#
# Methods to process article data

import logging
from entity_analysis import getEntities
from google.appengine.api import urlfetch
from aylienapiclient import textapi

aylienClient = textapi.Client('a5ad45d9', '2c891b3f58381a7842d500c5fb534b8e')

# Extract text from article urls
def processArticles(articles):
    results = []
    for article in articles[:5]:
        # Get title and text from article
        title, text, fullText = extractText(article['url'], aylienClient)

        # Perform entity analysis on text and title
        entities = getEntities(fullText)

        # If article didn't get at least 3 entities, don't include
        if len(entities) >= 3:
            # Get formatted JSON object for article
            articleObject = formatArticleJSON(title, article, entities)

            # Append article object to results
            results.append(articleObject)

    return results

# Aylien API call to extract title and text from article
def extractText(url, aylienClient):
    # Call alyien text API to extract text data and more from article url
    urlfetch.set_default_fetch_deadline(20)
    extract = aylienClient.Extract({'url': url, 'best_image': True})
    logging.debug('Extracted text successfully')

    # Get text and titles fields from extracted
    text = extract['article']
    title = extract['title']
    fullText = title + '. ' + text

    return title, text, fullText

# Formats the JSON object to return for single article
def formatArticleJSON(title, article, entities):
    articleObject = {
        'article': {
            'data': entities[:3],
            'title': title,
            'description': article['description'],
            'thumbnail': article['image']['thumbnail']['contentUrl'] if 'image' in article else 'null',
            'url': article['url'],
            'source': article['provider'][0]['name']
        }
    }
    return articleObject
