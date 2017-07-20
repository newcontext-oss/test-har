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
