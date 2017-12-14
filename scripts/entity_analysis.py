# entity_analysis
#
# Perform an entity sentiment analysis using Google Natural Language API

from apiclient import discovery

# Gets entity sentiment by calling Google Natural Language API, then filtering valid entities
def getEntitySentiment(text):
    # Make API call to Google to analyze entity sentiment
    entities = googleEntitySentiment(text)

    # Filter valid entities, ones with a wikipedia page
    entities = filterValidEntities(entities)

    return entities

# Gets entities by calling Google Natural Language API, then filtering valid entities
def getEntities(text):
    # Make API call to Google to analyze entity sentiment
    entities = googleEntities(text)

    # Filter valid entities, ones with a wikipedia page
    entities = filterValidEntities(entities)

    return entities

# Makes call to Google Natural Language API entity sentiment analysis
def googleEntitySentiment(text):
    # Declare components of call to Google Natural Language API
    APIKey = "AIzaSyDRhz9KsmomghOwZlIn-q7NZ76cf7JNTtg"
    body = {"document": {"type": "PLAIN_TEXT", "content": text }, "encodingType": "UTF8"}
    languageService = discovery.build('language', 'v1', developerKey=APIKey)

    # Make the API call, get entity sentiment
    result = languageService.documents().analyzeEntitySentiment(body=body).execute()

    return result['entities']

# Makes call to Google Natural Language API entity analysis
def googleEntities(text):
    # Declare components of call to Google Natural Language API
    APIKey = "AIzaSyDRhz9KsmomghOwZlIn-q7NZ76cf7JNTtg"
    body = {"document": {"type": "PLAIN_TEXT", "content": text }, "encodingType": "UTF8"}
    languageService = discovery.build('language', 'v1', developerKey=APIKey)

    # Make the API call, get entity sentiment
    result = languageService.documents().analyzeEntities(body=body).execute()

    return result['entities']

# Filters entities to return only those with wikipedia pages
def filterValidEntities(entities):
    validEntities = []
    for ent in entities:
        if 'wikipedia_url' in ent['metadata']:
            validEntities.append(ent)

    return validEntities
