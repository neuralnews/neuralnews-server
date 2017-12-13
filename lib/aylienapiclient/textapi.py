# Copyright 2016 Aylien, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import sys
import json
import aylienapiclient
from aylienapiclient.http import Request
from aylienapiclient.errors import HttpError
from aylienapiclient.errors import MissingParameterError
from aylienapiclient.errors import MissingCredentialsError

if sys.version_info >= (3, 0):
  basestring = str

class Client(object):
  """Constructor.
  
  Args:
    applicationId (str): Application ID.
    applicationKey (str): Application Key.
    useHttps (bool, optional): Whether to use HTTPS for web service calls.
      Defaults to True.

  Attributes:
    applicationId (str): Application ID.
    applicationKey (str): Application Key.
    useHttps (bool): Whether to use HTTPS for web service calls.
    normalizePattern (_sre.SRE_Pattern): Pattern to decide if string is
      URL or not.

  Raises:
    MissingCredentialsError: If applicationId or applicationKey are empty
  """
  def __init__(self, applicationId, applicationKey, useHttps=True):
    if not applicationId and not applicationKey:
      raise MissingCredentialsError('Invalid Application ID or Application Key.')

    self.applicationId = applicationId
    self.applicationKey = applicationKey
    self.useHttps = useHttps
    self.normalizePattern = re.compile(r"^https?://")
    self._lastResponseHeaders = dict()

  """Extracts the main body of article

  Extracts the main body of article, including embedded media such as
  images & videos from a URL and removes all the surrounding clutter.

  Args:
    options (dict):

      {
        'url (str)': URL,
        'best_image (bool)': Whether extract the best image of the article
      }

  Returns:
    A dict with these keys:

      {
        'title': 'string',
        'article': 'string',
        'image': 'string',
        'author': 'string',
        'videos': [],
        'feeds': []
      }

  Raises:
    aylienapiclient.errors.MissingParameterError if URL is missing.
  """
  def Extract(self, options):
    if isinstance(options, basestring):
      tmp = {}
      tmp['url'] = options
      options = tmp
    if 'url' not in options:
      raise MissingParameterError('You must provide a url')

    response = self._executeRequest('extract', options)

    return response

  """Classifies a piece of text.

  Classifies a piece of text according to IPTC NewsCode standard.

  Args:
    options (dict):
      {
        'url (str, optional)': URL,
        'text (str, optional)': Text,
        'language (str, optional)': Language of text. Valid options are
          en, de, fr, es, it, pt, and auto. If set to auto, it'll try to
          detect the language. Default is en.
      }

  Returns:
    A dict with these keys:

      {
        'text (str)': Text,
        'language (str)': Language of text,
        'categories (list)': [{
          'label (str)': Label of category,
          'code (str)': IPTC code
          'confidence (float)': Confidence
        }]
      }

  Raises:
    aylienapiclient.errors.MissingParameterError if both
      url and text are missing
  """
  def Classify(self, options):
    options = self._normalizeInput(options)
    if 'text' not in options and 'url' not in options:
      raise MissingParameterError('You must either provide url or text')

    response = self._executeRequest('classify', options)

    return response

  """Classifies a piece of text.

  Classifies a piece of text according to the specified taxonomy.

  Args:
    options (dict):
      {
        'url (str, optional)': URL,
        'text (str, optional)': Text,
        'language (str, optional)': Language of text.
        'taxonomy (str)': Taxonomy to classify according to.
      }

  Returns:
    A dict with these keys:

      {
        'text (str)': Text,
        'language (str)': Language of text,
        'categories (list)': [{
          'id (str)': ID of category,
          'label (str)': Label of category,
          'score (float)': Score of category,
          'confident (bool)': Confidence flag,
          'links (links)': [{
            'rel (string)': link relationship,
            'link (string)': linked resource
          }]
        }]
      }

  Raises:
    aylienapiclient.errors.MissingParameterError if both
      url and text are missing or taxonomy is not specified
  """
  def ClassifyByTaxonomy(self, options):
    options = self._normalizeInput(options)
    if 'text' not in options and 'url' not in options:
      raise MissingParameterError('You must either provide url or text')

    if 'taxonomy' not in options:
      raise MissingParameterError('You must specify the taxonomy')

    response = self._executeRequest('classify/' + options.pop('taxonomy'), options)

    return response

  """Extracts named entities mentioned in a document.

  Extracts named entities mentioned in a document, disambiguates and
  cross-links them to DBPedia and Linked Data entities, along with
  their semantic types (including DBPedia and schema.org).

  Args:
    options (dict):
      {
        'url (str, optional)': URL,
        'text (str, optional)': Text,
        'language (str, optional)': Language of text. Valid options are
          en, de, fr, es, it, pt, and auto. If set to auto, it'll try to
          detect the language. Default is en.
      }

  Returns:
    A dict with following structure:

      {
        'text (str)': Text,
        'language (str)': Language of text,
        'concepts (dict)': {
          concept: {
            surfaceForms: [{
              'string (str)': Surface form,
              'score (float)': Confidence score,
              'offset (int)': Offset in text
            }],
            'types (list of str)': Concept's types,
            'support (int)': Concept's importance. Higher is better.
          }
        }
      }

  Raises:
    aylienapiclient.errors.MissingParameterError if both
      url and text are missing
  """
  def Concepts(self, options):
    options = self._normalizeInput(options)
    if 'text' not in options and 'url' not in options:
      raise MissingParameterError('You must either provide url or text')

    response = self._executeRequest('concepts', options)

    return response

  """Extracts named entities and values in a document.

  Extracts named entities (people, organizations and locations) and
  values (URLs, emails, telephone numbers, currency amounts and percentages)
  mentioned in a body of text.

  Args:
    options (dict):
      {
        'url (str, optional)': URL,
        'text (str, optional)': Text
      }

  Returns:
    A dict with following structure:

      {
        'text (str)': Text,
        'entities (dict)': {
          'person (list of str, optional)': Persons,
          'organization (list of str, optional)': Organization,
          'location (list of str, optional)': Locations,
          'keyword (list of str, optional)': Keywords,
          'date (list of str, optional)': Dates,
          'percentage (list of str, optional)': Percentages,
          'money (list of str, optional)': Money,
          'product (list of str, optional)': Products
        }
      }

  Raises:
    aylienapiclient.errors.MissingParameterError if both
      url and text are missing
  """
  def Entities(self, options):
    options = self._normalizeInput(options)
    if 'text' not in options and 'url' not in options:
      raise MissingParameterError('You must either provide url or text')

    response = self._executeRequest('entities', options)

    return response

  """Suggests hashtags describing the document.

  Args:
    options (dict):
      {
        'url (str, optional)': URL,
        'text (str, optional)': Text,
        'language (str, optional)': Language of text. Valid options are
          en, de, fr, es, it, pt, and auto. If set to auto, it'll try to
          detect the language. Default is en.
      }

  Returns:
    A dict with following structure:

      {
        'text (str)': Text,
        'language (str)': Language of text,
        'hashtags (list of str)': List of hashtags
      }

  Raises:
    aylienapiclient.errors.MissingParameterError if both
      url and text are missing
  """
  def Hashtags(self, options):
    options = self._normalizeInput(options)
    if 'text' not in options and 'url' not in options:
      raise MissingParameterError('You must either provide url or text')

    response = self._executeRequest('hashtags', options)

    return response

  """Detects the main language a document is written in.

  Detects the main language a document is written in and returns it
  in ISO 639-1 format.

  Args:
    options (dict):
      {
        'url (str, optional)': URL,
        'text (str, optional)': Text,
      }

  Returns:
    A dict with following structure:

      {
        'text (str)': Text,
        'lang (str)': Language code in ISO 639-1 format,
        'confidence (float)': Confidence of calculation
      }

  Raises:
    aylienapiclient.errors.MissingParameterError if both
      url and text are missing
  """
  def Language(self, options):
    options = self._normalizeInput(options)
    if 'text' not in options and 'url' not in options:
      raise MissingParameterError('You must either provide url or text')

    response = self._executeRequest('language', options)

    return response

  """Returns phrases related to the provided unigram, or bigram.

  Args:
    options (dict):
      {
        'phrase (str)': Phrase,
        'count (int, optional)': Number of phrases to return.
          Default is 20. Max is 100.
      }

  Returns:
    A dict with following structure:

      {
        'phrase (str)': Phrase,
        'related (list of dict)': [{
          'phrase (str)': Related phrase,
          'distance (float)': Distance
        }]
      }

  Raises:
    aylienapiclient.errors.MissingParameterError if both
      phrase is missing.
  """
  def Related(self, options):
    if isinstance(options, basestring):
      tmp = {}
      tmp['phrase'] = options
      options = tmp
    if 'phrase' not in options:
      raise MissingParameterError('You must provide a phrase')

    response = self._executeRequest('related', options)

    return response

  """Detects sentiment of a body of text.

  Detects sentiment of a document in terms of
  polarity ("positive" or "negative") and
  subjectivity ("subjective" or "objective").

  Args:
    options (dict):
      {
        'mode (str, optional)': Analyze mode. Valid options are
          tweet, and document. Default is tweet.
        'text (str, optional'): Text,
        'url (str, optional'): URL
      }

  Returns:
    A dict with following structure:

      {
        'text (str)': Text,
        'subjectivity (str)': Subjectivity. subjective, or objective.
        'subjectivity_confidence (float)': Confidence of evaluation.
        'polarity (str)': Polarity. positive, or negative.
        'polarity_confidence (float)': Confidence of evaluation.
      }

  Raises:
    aylienapiclient.errors.MissingParameterError if both
      url and text are missing
  """
  def Sentiment(self, options):
    options = self._normalizeInput(options)
    if 'text' not in options and 'url' not in options:
      raise MissingParameterError('You must either provide url or text')

    response = self._executeRequest('sentiment', options)

    return response

  """Detects aspects and sentiment of a body of text.

  Given a review for a product or service, analyzes the sentiment of the
  review towards each of the aspects of the product or review that are
  mentioned in it.

  Args:
    options (dict):
      {
        'url (str, optional)': URL,
        'text (str, optional)': Text,
        'domain (str)': Domain which document belongs to
      }

  Returns:
    A dict with these keys:

      {
        'text (str)': Text,
        'domain (str)': Domain,
        'aspects (list)': [{
            'aspect (str)': Aspect,
            'aspect_confidence (float)': Confidence of aspect,
            'polarity (str)': Aspect polarity,
            'polarity_confidence (float)': Confidence of aspect polarity
        }],
        'sentences (list)': [{
            'text (str)': Sentence text,
            'polarity (str)': Sentence polarity,
            'polarity_confidence (float)': Confidence of sentence polarity,
            'aspects (list)': [{
                'aspect (str)': Aspect,
                'aspect_confidence (float)': Confidence of aspect,
                'polarity (str)': Aspect polarity,
                'polarity_confidence (float)': Confidence of aspect polarity
            }],
        }]
      }

  Raises:
    aylienapiclient.errors.MissingParameterError if both
      url and text are missing or domain is not specified
  """
  def AspectBasedSentiment(self, options):
    options = self._normalizeInput(options)
    if 'text' not in options and 'url' not in options:
      raise MissingParameterError('You must either provide url or text')

    if 'domain' not in options:
      raise MissingParameterError('You must specify the domain')

    response = self._executeRequest('absa/' + options.pop('domain'), options)

    return response

  """Summarizes an article into a few key sentences.

  Args:
    options (dict):
      {
        'mode (str, optional)': Analyze mode. Valid options are default
          and short. Default is default. short mode produces shorter
          sentences.
        'text (str, optional)': Text,
        'title (str, optional)': Title,
        'url (str, optional)': URL,
        'sentences_number': Number of sentences to be returned.
          Only in default mode (not applicable to short mode).
          Default value is 5.
          has precedence over sentences_percentage.
        'sentences_percentage': Percentage of sentences to be returned.
          Only in default mode (not applicable to short mode).
          Possible range is 1-100.
          sentences_number has precedence over this parameter.
      }

  Returns:
    A dict with following structure:

      {
        'text (str)': Text,
        'sentences (list of str)': Key sentences
      }

  Raises:
    aylienapiclient.errors.MissingParameterError if both
      url and text are missing
  """
  def Summarize(self, options):
    options = self._normalizeInput(options)
    if 'text' not in options and 'url' not in options:
      raise MissingParameterError('You must either provide url or text')

    response = self._executeRequest('summarize', options)

    return response


  """Extracts microformats.

  Args:
    options (dict):

      {
        'url (str)': URL
      }

  Returns:
    A dict with these keys:

      {
        'hCards (list of hCard)': hCards
      }
  Raises:
    aylienapiclient.errors.MissingParameterError if url
      is missing
  """
  def Microformats(self, options):
    options = self._normalizeInput(options)
    if 'url' not in options:
      raise MissingParameterError('You must provide a url')

    response = self._executeRequest('microformats', options)

    return response

  """Assigns relevant tag to an image.

  Args:
    options (dict):

      {
        'url (str)': URL
      }

  Returns:
    A dict with these keys:

      {
        'image (str)': Image URL,
        'tags (list of dict)': [{
          'tag (str)': Tag name,
          'confidence (float)': Confidence
        }]
      }

  Raises:
    aylienapiclient.errors.MissingParameterError if url
      is missing
  """
  def ImageTags(self, options):
    options = self._normalizeInput(options)
    if 'url' not in options:
      raise MissingParameterError('You must provide a url')

    response = self._executeRequest('image-tags', options)

    return response

  """Picks the most semantically relevant class label or tag.

  Args:
    options (dict):

      {
        'url (str, optional)': URL,
        'text (str, optional)': Text,
        'class (list of str)': List of classes to classify into,
        'number_of_concepts (int, optional)': Specify the number
          of concepts used to measure the semantic similarity
          between two words
      }

  Returns:
    A dict with following structure:

      {
        'text (str)': Text,
        'classes (list of dict)': [{
          'label (str)': Class label,
          'score (float)': Score
        }]
      }

  Raises:
    aylienapiclient.errors.MissingParameterError if both
      url and text are missing
  """
  def UnsupervisedClassify(self, options):
    options = self._normalizeInput(options)
    if 'text' not in options and 'url' not in options:
      raise MissingParameterError('You must either provide url or text')

    response = self._executeRequest('classify/unsupervised', options)

    return response

  """Runs multiple analysis operations in one API call.

  Args:
    options (dict):

      {
        'url (str, optional)': URL,
        'text (str, optional)': Text,
        'endpoint (list of str)': List of operations
      }

  Returns:
    A dict with following structure:

      {
        'text (str)': Text,
        'results (list of dict)': [{
          'endpoint (str)': Endpoint
          'result (dict)': Endpoint result. Structure follows their respective
            individual calls.
        }]
      }

  Raises:
    aylienapiclient.errors.MissingParameterError if both
      url and text are missing
  """
  def Combined(self, options):
    options = self._normalizeInput(options)
    if 'text' not in options and 'url' not in options:
      raise MissingParameterError('You must either provide url or text')

    response = self._executeRequest('combined', options)

    return response

  """Returns current client's rate limit values.

  Relies on the HTTP headers of the last response so it's empty on cold start.
  Making some calls will populate ratelimit fields.

  Returns:
    A dict with following structure:

      {
        'limit (int)': Limit,
        'reset (int)': Unix UTC timestamp indicating the exact time remaining resets,
        'remaining (int)': Remaining calls
      }
  """
  def RateLimits(self):
    return dict((k.replace("x-ratelimit-", ""), int(v)) for (k, v) in self._lastResponseHeaders.items() if "x-ratelimit-" in k)

  """Executes a request.

  Returns: dict

  Raises:
    aylienapiclient.errors.HttpError if HTTP data is invalid
      or unexpected.
  """
  def _executeRequest(self, endpoint, params):
    request = self._buildRequest(endpoint, params)
    response, content = request.execute()
    self._lastResponseHeaders = response

    if response.status >= 300:
      raise HttpError(response, content, uri=request.uri)
    
    if sys.version_info >= (3, 0):
      unmarshalled = json.loads(content.decode())
    else:
      unmarshalled = json.loads(content)

    return unmarshalled

  """Builds a request.

  Returns:
    aylienapiclient.http.Request
  """
  def _buildRequest(self, endpoint, params):
    headers = {
        'Accept': 'application/json',
        'Content-type': 'application/x-www-form-urlencoded',
        'X-AYLIEN-TextAPI-Application-ID': self.applicationId,
        'X-AYLIEN-TextAPI-Application-Key': self.applicationKey,
        'User-Agent': "Aylien Text API Python " + aylienapiclient.__version__
        }
    request = Request(endpoint, params, headers, self.useHttps)

    return request

  """Normalizes input.

  If input type is str it'll try to make a dict out of it by either
  setting a 'text', or 'url' key based on the format of string.

  Returns: dict
  """
  def _normalizeInput(self, input):
    if isinstance(input, basestring):
      param = 'url' if self.normalizePattern.match(input) else 'text'
      return {param: input}
    else:
      return input
