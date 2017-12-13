# main.py
#
# Main entry point for the app

from flask import Flask, render_template
import httplib, urllib, json, logging, datetime
from scripts.article_processing import processArticles
from scripts.news_search import bingNewsSearch

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/trendingtopics')
def trendingtopics():
    return app.open_resource('trendingtopics.json').read()

@app.route('/hometopics')
def hometopics():
    # Read trending topics from JSON file
    return json.dumps(json.loads(app.open_resource('hometopics.json').read()))


    topics = app.open_resource('trendingtopics.json').read()
    topics = json.loads(topics)

    # For each topic, get articles, and append to result list
    results = []
    for topic in topics:
        # Search news for topic
        responseObject = bingNewsSearch(topic)
        articles = responseObject['value']

        # Process article data
        processedArticles = processArticles(articles)

        # Define JSON object for topic and append to result
        topicObject = {
            'topic': topic,
            'articles': processedArticles
        }
        results.append(topicObject)

    return json.dumps(results)


@app.route('/query/')
@app.route('/query/<query>')
def query(query=None):
    # Search news for query using Bing API
    responseObject = bingNewsSearch(query)
    articles = responseObject['value']

    # Process article data
    processedArticles = processArticles(articles)

    return json.dumps(processedArticles)

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally
    app.run(host='127.0.0.1', port=8080, debug=True)
