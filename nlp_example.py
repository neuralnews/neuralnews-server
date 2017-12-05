# nlp example

# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

# Instantiates a client
client = language.LanguageServiceClient()

# The text to analyze
text = u'Donald Trump is the worst president of the United States I\'ve ever seen! Trump needs to leave now! Hillary Clinton was the best candidate anyone could have asked for.'
document = types.Document(
    content=text,
    type=enums.Document.Type.PLAIN_TEXT)

result = client.analyze_entity_sentiment(document)

print(text)
for entity in result.entities:
    print('Mentions: ')
    print(u'Name: "{}"'.format(entity.name))
    for mention in entity.mentions:
        print(u'  Begin Offset : {}'.format(mention.text.begin_offset))
        print(u'  Content : {}'.format(mention.text.content))
        print(u'  Magnitude : {}'.format(mention.sentiment.magnitude))
        print(u'  Sentiment : {}'.format(mention.sentiment.score))
        print(u'  Type : {}'.format(mention.type))
    print(u'Salience: {}'.format(entity.salience))
    print(u'Sentiment: {}\n'.format(entity.sentiment))
