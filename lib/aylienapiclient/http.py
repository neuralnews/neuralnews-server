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

"""Class to encapsulate a single HTTP request.

Every object supports an execute() method that
does the actual HTTP request.
"""

import sys
import httplib2
import platform

if sys.version_info >= (3, 0):
  from urllib.parse import urlencode
else:
  from urllib import urlencode

class Request(object):
  """Encapsulates a single HTTP request."""

  API_V1_HOST_AND_PATH = 'api.aylien.com/api/v1';
  
  def __init__(self, endpoint, params={}, headers=None, isHttps=True):
    """Constructor for a Request.
    """
    self._uri = None

    self.headers = headers
    self.isHttps = isHttps
    self.endpoint = endpoint
    self.uri = endpoint
    self.http = httplib2.Http()
    self.params = params

  def execute(self):
    body = urlencode([(k, v) for k, vs in self.params.items() for v in isinstance(vs, list) and vs or [vs]])
    return self.http.request(self.uri, 'POST', headers=self.headers, body=body)

  @property
  def uri(self):
    return self._uri

  @uri.setter
  def uri(self, value):
    protocol = 'https' if self.isHttps else 'http'
    self._uri = "%s://%s/%s" % (protocol, self.API_V1_HOST_AND_PATH, value)
