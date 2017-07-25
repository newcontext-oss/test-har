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
        # Insert a key into the response
        # about which HAR response makes no assertion
        content = dict(
            self.entry["response"]["content"]["text"],
            email='foo@example.com')
        self.mocker.post(
            self.entry["request"]["url"],
            status_code=self.entry["response"]["status"],
            reason=self.entry["response"]["statusText"],
            headers=self.headers,
            text=json.dumps(content))

    def test_non_json(self):
        """
        Mock the requests library non-JSON response.
        """
        self.entry["response"]["content"]["mimeType"] = "text/html"
        self.entry["response"]["content"]["text"] = (
            '<html><body>Foo HTML body</body></html>')
        self.mocker.post(
            self.entry["request"]["url"],
            status_code=self.entry["response"]["status"],
            reason=self.entry["response"]["statusText"],
            headers=dict(self.headers, **{'Content-Type': self.entry[
                "response"]["content"]["mimeType"]}),
            text=self.entry["response"]["content"]["text"])
        super(HARDogfoodRequestsTests, self).test_non_json()

    def test_missing_content_type(self):
        """
        Fail when the response is missing the content/MIME type.
        """
        self.headers.pop('Content-Type')
        self.mocker.post(
            self.entry["request"]["url"],
            status_code=self.entry["response"]["status"],
            reason=self.entry["response"]["statusText"],
            headers=self.headers,
            text=json.dumps(self.entry["response"]["content"]["text"]))

        with self.assertRaises(AssertionError) as har_failures:
            self.assertHAR(self.example)

        self.assertIn(
            'content/mimeType', har_failures.exception.args[0],
            'Assertion exception missing MIME type detail')
        # BBB Python 2.7 str vs unicode compat
        with self.assertRaises(AssertionError) as expected:
            self.assertIn(
                'Content-Type', self.headers,
                'Missing response content type')
        self.assertEqual(
            har_failures.exception.args[0]['content/mimeType'].args,
            expected.exception.args,
            'Wrong missing response MIME type failure assertion')
