import requests

import test_har
from test_har import *  # noqa


class HARTestCase(test_har.HARTestCase):
    """
    Run tests using HTTP Archive (HAR) files through the requests library.
    """

    def _request_har(self, method, url, headers):
        """
        Send the request using the requests library.
        """
        request_method = getattr(requests, method.lower())
        return request_method(url, headers=headers)
