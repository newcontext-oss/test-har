"""
Test using HAR files in Python tests against the Django ReST framework.
"""

from django import http

from rest_framework import response

from test_har import django_rest_har as test_har
from test_har import tests


class HARDogfoodDRFTests(tests.HARDogfoodTestCase, test_har.HARTestCase):
    """
    Test using HAR files in Python tests against the Django ReST framework.
    """

    RESPONSE_TYPE = (http.HttpResponse, response.Response)

    def test_runner(self):
        """
        Ensure tests are running.
        """
        self.assertTrue(True)
