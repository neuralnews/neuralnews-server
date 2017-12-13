# news_search.py
#
# Module to search for news using Bing API

import httplib, urllib, json, logging, datetime

# Microsoft Azure Cognitive Services variables
subscriptionKey = 'bfc96e2d7cee4696b2e3bd85c2f4816c'
host = 'api.cognitive.microsoft.com'
path = '/bing/v7.0/news/search'
headers = {'Ocp-Apim-Subscription-Key': subscriptionKey}

# Performs the API call to the Bing News Search API
def bingNewsSearch(search):
    "Performs a Bing Web search and returns the results."
    logging.debug('Searching news for: ' + search)
    conn = httplib.HTTPSConnection(host)
    query = urllib.quote(search)
    conn.request("GET", path + "?q=" + query, headers=headers)
    response = conn.getresponse()
    return json.loads(response.read())
