# data_processing.py
#
# Methods to process article data

import logging, json
from entity_analysis import getEntities
from google.appengine.api import urlfetch
from aylienapiclient import textapi
from google.cloud import bigquery
import requests_toolbelt.adapters.appengine

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()

aylienClient = textapi.Client('a5ad45d9', '2c891b3f58381a7842d500c5fb534b8e')
bigqueryClient = bigquery.Client(project='neural-news-186322')

# Extract text from article urls
def processArticles(articles):
    # Get saved articles from database
    savedArticles = queryTable(articles)

    results = [] # final list to return
    newRows = [] # list of rows of new articles to add to database
    for article in articles[:5]:
        # If saved, don't re-compute analysis. Append saved analysis
        if article['url'] in savedArticles:
            print('FOUND SAVED')
            results.append(json.dumps(savedArticles[article['url']]))
            print(json.dumps(savedArticles[article['url']]))
        else:
            print('NOT SAVED')
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

                # Append to new rows
                newRows.append((article['url'], json.dumps(articleObject)))

    if newRows:
        addtoTable(newRows)

    return results

# Query BigQuery database to return data already cached for article urls
def queryTable(articles):
    # Declare format string for query each article url
    formatString = 'url = \"{}\"'.format(articles[0]['url'])
    for article in articles[1:]:
        formatString += ' OR url = \"{}\"'.format(article['url'])

    print(formatString)

    # Check if article in database
    query = """
        #standardSQL
        SELECT url, json_data
        FROM neuralnews.article_data
        WHERE {};
        """.format(formatString)
    query_job = bigqueryClient.query(query)
    queryResults = query_job.result()    # API call
    print('Results recieved')

    # Construct a dictionary for the results
    finalResults = {}
    for row in queryResults:
        finalResults[row.url] = json.loads(row.json_data)

    return finalResults

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
            'thumbnail': article['image']['thumbnail']['contentUrl'] if 'image' in article else 'https://news.stanford.edu/news/2016/february/images/16087-opiates_news.jpg',
            'url': article['url'],
            'source': article['provider'][0]['name']
        }
    }
    return articleObject

# Adds article data to BigQuery database
def addtoTable(rows):
    # Get table from BigQuery
    dataset = bigqueryClient.dataset('neuralnews')
    table = dataset.table('article_data')
    table = bigqueryClient.get_table(table)

    # Add rows to table
    errors = bigqueryClient.create_rows(table, rows)
    assert errors == []
    print(errors)
    print(rows)
