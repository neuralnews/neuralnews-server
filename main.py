# main.py
#
# Main entry point for the app

from flask import Flask, render_template
from aylienapiclient import textapi
import httplib, urllib, json, logging, datetime
from scripts.data_processing import processArticles

aylienClient = textapi.Client('a5ad45d9', '2c891b3f58381a7842d500c5fb534b8e')


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/trendingtopics')
def trendingtopics():
    with app.open_resource('trendingtopics.json') as f:
        return f.read()

@app.route('/query/')
@app.route('/query/<query>')
def query(query=None):
    # Microsoft Azure Cognitive Services variables
    subscriptionKey = 'bfc96e2d7cee4696b2e3bd85c2f4816c'
    host = 'api.cognitive.microsoft.com'
    path = '/bing/v7.0/news/search'
    headers = {'Ocp-Apim-Subscription-Key': subscriptionKey}
    startDate = datetime.date

    def bingNewsSearch(search):
        "Performs a Bing Web search and returns the results."
        logging.debug('Searching news for: ' + search)
        conn = httplib.HTTPSConnection(host)
        query = urllib.quote(search)
        conn.request("GET", path + "?q=" + query, headers=headers)
        response = conn.getresponse()
        return json.loads(response.read())

    responseObject = bingNewsSearch(query)
    articles = responseObject['value']

    return json.dumps(processArticles(articles, startDate, aylienClient))

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
