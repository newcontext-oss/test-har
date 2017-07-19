"""
Test using HAR files in Python tests against the requests library.
"""

import json

import requests
import requests_mock

from test_har import requests_har as test_har
from test_har import tests


class HARDogfoodRequestsTests(tests.HARDogfoodTestCase, test_har.HARTestCase):
    """
    Test using HAR files in Python tests against the requests library.
    """

    RESPONSE_TYPE = requests.Response

    def setUp(self):
        """
        Start the mocker, mock the example HAR response, and register cleanup.
        """
        super(HARDogfoodRequestsTests, self).setUp()

        self.mocker = requests_mock.Mocker()
        self.mocker.start()
        self.addCleanup(self.mocker.stop)

        self.headers = test_har.array_to_dict(
            self.entry["response"]["headers"])
        self.headers['Content-Type'] = self.entry[
            "response"]["content"]["mimeType"]
        self.mocker.post(
            self.entry["request"]["url"],
            status_code=self.entry["response"]["status"],
            reason=self.entry["response"]["statusText"],
            headers=self.headers,
            text=json.dumps(self.entry["response"]["content"]["text"]))

    def test_runner(self):
        """
        Ensure tests are running.
        """
        self.assertTrue(True)

    def test_non_json(self):
        """
        Mock the requests library non-JSON response.
        """
        self.entry["response"]["content"]["mimeType"] = "text/plain"
        self.entry["response"]["content"]["text"] = 'Foo plain text body'
        self.mocker.post(
            self.entry["request"]["url"],
            status_code=self.entry["response"]["status"],
            reason=self.entry["response"]["statusText"],
            headers=dict(self.headers, **{'Content-Type': self.entry[
                "response"]["content"]["mimeType"]}),
            text=self.entry["response"]["content"]["text"])
        super(HARDogfoodRequestsTests, self).test_non_json()
