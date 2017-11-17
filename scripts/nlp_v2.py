# -*- coding: utf-8 -*-
# neural_news
#from textblob import TextBlob
import json
import sys

# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

def analysis(text):
    # Instantiates a client
    client = language.LanguageServiceClient()

    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    analysis_result = client.analyze_entity_sentiment(document)
    final_result = []

    for entity in analysis_result.entities:
        #print('Mentions: ')
        #print(u'Name: "{}"'.format(entity.name))
        current_ent = {
            'name'      :   entity.name,
            'mentions'  :   [],
        }
        for mention in entity.mentions:
            #print(u'  Begin Offset : {}'.format(mention.text.begin_offset))
            #print(u'  Content : {}'.format(mention.text.content))
            #print(u'  Magnitude : {}'.format(mention.sentiment.magnitude))
            #print(u'  Sentiment : {}'.format(mention.sentiment.score))
            #print(u'  Type : {}'.format(mention.type))
            current_ent['mentions'].append({
                'begin_offset'  :   mention.text.begin_offset,
                'content'       :   mention.text.content,
                'magnitude'     :   mention.sentiment.magnitude,
                'sentiment'     :   mention.sentiment.score,
                'type'          :   mention.type,
            })
        #print(u'Salience: {}'.format(entity.salience))
        current_ent['salience'] = entity.salience
        #print(u'Magnitude: {}\n'.format(entity.sentiment.magnitude))
        current_ent['magnitude'] = entity.sentiment.magnitude
        #print(u'Sentiment: {}\n'.format(entity.sentiment.score))
        current_ent['sentiment'] = entity.sentiment.score
        final_result.append(current_ent)

    # Detects entities in the document. You can also analyze HTML with:
    #   document.type == enums.Document.Type.HTML
    entities = client.analyze_entities(document).entities

    # entity types from enums.Entity.Type
    entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION',
                   'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER')

    #raw_ents = []
    for entity in entities:
        current_ent = {
            'name'          :   entity.name,
            'type'          :   entity.type,
            'metadata'      :   entity.metadata,
            'salience'      :   entity.salience,
            'wikipedia_url' :   entity.metadata.get('wikipedia_url', '-'),
        }
        #print('=' * 20)
        #print(u'{:<16}: {}'.format('name', entity.name))
        #print(u'{:<16}: {}'.format('type', entity_type[entity.type]))
        #print(u'{:<16}: {}'.format('metadata', entity.metadata))
        #print(u'{:<16}: {}'.format('salience', entity.salience))
        #print(u'{:<16}: {}'.format('wikipedia_url', entity.metadata.get('wikipedia_url', '-')))

        #raw_ents.append(current_ent)
        final_result.append(raw_ents)

    print(json.dumps(final_result))
    sys.stdout.flush()

def main():
    article = sys.argv[1]
    analysis(article)

if __name__ == "__main__":
    main()
