# -*- coding: utf-8 -*-
# neural_news
#from textblob import TextBlob
import json
import sys
sys.path.insert(0, 'lib')
import logging

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

    # Raw entities
    entities = client.analyze_entities(document).entities

    # entity types from enums.Entity.Type
    entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION',
                   'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER')

    final_result = []       # Final return list
    raw_ents = {}           # Dictionary of valid raw ents

    # Filter valid entities
    for entity in entities:
        current_ent = {
            'name'          :   entity.name,
            'type'          :   entity_type[entity.type],
            'salience'      :   entity.salience,
            'wikipedia_url' :   entity.metadata.get('wikipedia_url', '-'),
        }

        # Don't add unless entity has wikipedia
        if current_ent['wikipedia_url'] != '-':
            raw_ents[current_ent['name']] = current_ent

    analysis_result = client.analyze_entity_sentiment(document)

    for entity in analysis_result.entities:
        current_ent = {
            'name'      :   entity.name,
            'mentions'  :   [],
        }
        if current_ent['name'] in raw_ents:
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
            current_ent['wikipedia_url'] = raw_ents[current_ent['name']]['wikipedia_url']
            final_result.append(current_ent)

    print(json.dumps(final_result))
    sys.stdout.flush()

def main():
    article = sys.argv[1]
    analysis(article)

if __name__ == "__main__":
    main()
