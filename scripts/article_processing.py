# data_processing.py
#
# Methods to process article data

import logging, json
from entity_analysis import getEntitySentiment, getEntities
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
def processArticles(articles, query):
    # Get saved articles from database
    savedArticles = queryTable(articles)

    # Get sentiment about query -- only one entity for now
    queryEntity = getEntities(query)
    queryEntity = queryEntity[0] if queryEntity else queryEntity

    results = [] # list of article objects
    negative = [] # negative on query
    neutral = [] # neutral on query
    positive = [] # positive on query
    newRows = [] # list of rows of new articles to add to database
    print('ARTICLE LENGTH:' + ' ' + str(len(articles)))
    for article in articles:
        # If saved, don't re-compute analysis. Append saved analysis
        if article['url'] in savedArticles:
            print('FOUND SAVED')
            articleObject = savedArticles[article['url']]
            #results.append(json.dumps(articleObject))
            print(json.dumps(savedArticles[article['url']]))
        else:
            print('NOT SAVED')
            # Get title and text from article
            title, text, fullText = extractText(article['url'], aylienClient)

            # Perform entity analysis on text and title
            entities = getEntitySentiment(fullText)

            # If article didn't get at least 3 entities, don't include
            if len(entities) >= 3:
                # Get formatted JSON object for article
                articleObject = formatArticleJSON(title, article, entities)

                # Append article object to results
                #results.append(articleObject)

                # Append to new rows
                newRows.append((article['url'], json.dumps(articleObject)))

        print('QUERY')
        print(queryEntity)
        if queryEntity:
            for ent in articleObject['article']['data']:
                print('ENT')
                print(ent)
                if queryEntity['name'] == ent['name'] or ('wikipedia_url' in queryEntity['metadata'] and queryEntity['metadata']['wikipedia_url'] == ent['metadata']['wikipedia_url']):
                    articleObject['article']['querySentiment'] = ent['sentiment']['score'] * ent['sentiment']['magnitude']
                    if ent['sentiment']['score'] < 0:
                        print('NEG')
                        negative.append(articleObject)
                        negative = sorted(negative, key=lambda articleObject: articleObject['article']['querySentiment'])
                    elif ent['sentiment']['score'] > 0:
                        print('POS')
                        positive.append(articleObject)
                        positive = sorted(positive, key=lambda articleObject: articleObject['article']['querySentiment'])
                    else:
                        print('NEUTRAL')
                        neutral.append(articleObject)

            if 'querySentiment' not in articleObject['article']:
                print('NOT FOUND')
                articleObject['article']['querySentiment'] = 0
                neutral.append(articleObject)
        else:
            print('NO QUERY')
            articleObject['article']['querySentiment'] = 0
            neutral.append(articleObject)

    # If new rows, add to table
    if newRows:
        addtoTable(newRows)

    print('LEN POS:' + ' ' + str(len(positive)))
    print('LEN NEG:' + ' ' + str(len(negative)))
    print('LEN NEUT:' + ' ' + str(len(neutral)))

    results.extend(negative)
    results.extend(neutral)
    results.extend(positive)

    startingIndex = len(negative) + len(neutral) / 2

    # Create JSON object to be returned
    finalResult = {
        'startingIndex': startingIndex,
        'articles': results
    }

    return finalResult

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
    # Call alyien text API
    urlfetch.set_default_fetch_deadline(10)
    extracted = False
    while not extracted:
        try:
            extract = aylienClient.Extract({'url': url, 'best_image': True})
            print('Extracted text successfully.')
            extracted = True
        except:
            print('Extraction Failed. Trying Again.')

    # Get text and titles fields from extracted
    text = extract['article']
    title = extract['title']
    fullText = title + '. ' + text

    return title, text, fullText

# Formats the JSON object to return for single article
def formatArticleJSON(title, article, entities):
    articleObject = {
        'article': {
            'data': entities,
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
    #print(rows)
