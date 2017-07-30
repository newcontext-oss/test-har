import json

from rest_framework import test

import test_har
from test_har import *  # noqa


class HARDRFTestCase(test.APITestCase, test_har.HARTestCase):
    """
    Run tests using HTTP Archive (HAR) files through the Django ReST Framework.
    """

    def request_har(self, method, url, data=None, **kwargs):
        """
        Send the request using the Django ReST Framework.
        """
        headers = kwargs.pop('headers', {})

        content_type = headers.pop('Content-Type', None)
        if content_type is not None:
            kwargs['content_type'] = content_type
            if self.JSON_MIME_TYPE_RE.match(content_type) is not None:
                data = json.dumps(data)

        kwargs.update(
            ('HTTP_{0}'.format(key.upper()), value)
            for key, value in headers.items())

        request_method = getattr(self.client, method.lower())
        response = request_method(url, data=data, **kwargs)
        return response

    def get_reason(self, response):
        """
        Lookup the Django ReST Framework response reason phrase.
        """
        return response.reason_phrase

    def get_headers(self, req_or_resp):
        """
        Lookup the Django ReST Framework headers on a request or response.
        """
        return dict(req_or_resp.items())

    def get_text(self, response):
        """
        Lookup the Django ReST Framework response body text.
        """
        return response.content.decode()


HARTestCase = HARDRFTestCase
