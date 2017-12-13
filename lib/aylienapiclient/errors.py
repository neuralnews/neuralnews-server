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

"""Errors for the library.

All exceptions defined by the library
should be defined in this file.
"""

import json

class Error(Exception):
  """Base error for this module."""
  pass

class MissingParameterError(Error):
  """Required parameters is missing"""
  pass

class MissingCredentialsError(Error):
  """API credentials are missing"""
  pass

class HttpError(Error):
  """HTTP data was invalid or unexpected."""

  def __init__(self, resp, content, uri=None):
    self.resp = resp
    self.content = content
    self.uri = uri

  def _get_reason(self):
    reason = self.resp.reason
    try:
      data = json.loads(self.content)
      reason = data['error']
    except (ValueError, KeyError):
      if self.resp.status == 403:
        reason = self.content
      else:
        pass

    if reason is None:
      reason = ''

    return reason

  def __repr__(self):
    if self.uri:
      return '<HttpError %s when requesting %s returned "%s">' % (
          self.resp.status, self.uri, self._get_reason().strip())
    else:
      return '<HttpError %s "%s">' % (self.resp.status, self._get_reason().strip())

  __str__ = __repr__
