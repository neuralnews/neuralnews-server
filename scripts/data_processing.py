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
        # Get title and text from article
        title, text, fullText = extractText(article['url'], aylienClient)

        # Perform entity analysis on text and title
        entities = analyzeEntitySentiment(fullText, startDate)

        # Get formatted JSON object for article
        articleObject = formatArticleJSON(title, article, entities)

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
            'data': entities[:5] if len(entities) >= 5 else entities,
            'title': title,
            'description': article['description'],
            'thumbnail': article['image']['thumbnail']['contentUrl'] if 'image' in article else 'null',
            'url': article['url'],
            'source': article['provider'][0]['name']
        }
    }
    return articleObject
