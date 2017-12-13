# entity_analysis
#
# Perform an entity sentiment analysis using Google Natural Language API

from apiclient import discovery

def analyzeEntitySentiment(text, startDate):
    # Make API call to Google to analyze entity sentiment
    entities = googleEntitySentiment(text)

    # Filter valid entities, ones with a wikipedia page
    entities = filterValidEntities(entities)

    return entities

# Makes call to Google Natural Language API entity sentiment analysis
def googleEntitySentiment(text):
    # Declare components of call to Google Natural Language API
    APIKey = "AIzaSyDRhz9KsmomghOwZlIn-q7NZ76cf7JNTtg"
    body = {"document": {"type": "PLAIN_TEXT", "content": text }, "encodingType": "UTF8"}
    languagService = discovery.build('language', 'v1', developerKey=APIKey)

    # Make the API call, get entity sentiment
    entities = languageService.documents().analyzeEntitySentiment(body=body).execute()

    return entities

# Filters entities to return only those with wikipedia pages
def filterValidEntities(entities):
    validEntities
    for ent in entities:
        if 'wikipedia_url' in entities['metadata']:
            validEntities.append(ent)

    return validEntities
