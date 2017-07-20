import requests

import test_har
from test_har import *  # noqa


class HARRequestsTestCase(test_har.HARTestCase):
    """
    Run tests using HTTP Archive (HAR) files through the requests library.
    """

    def request_har(self, method, url, data=None, **kwargs):
        """
        Send the request using the requests library.
        """
        request_method = getattr(requests, method.lower())
        return request_method(url, data=data, **kwargs)

    def get_reason(self, response):
        """
        Lookup the requests library response reason phrase.
        """
        return response.reason

    def get_headers(self, req_or_resp):
        """
        Lookup the requests library headers on a request or response.
        """
        return req_or_resp.headers

    def get_text(self, response):
        """
        Lookup the requests library response body text.
        """
        return response.text


HARTestCase = HARRequestsTestCase
