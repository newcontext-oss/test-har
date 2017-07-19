"""
Test using HAR files in Python tests.
"""

from __future__ import unicode_literals

import os
import json
import copy

import test_har


class HARDogfoodTestCase(object):
    """
    Tests common to all backends.
    """

    # Subclasses must define
    # RESPONSE_TYPE = ...

    def setUp(self):
        """
        Load an example HAR file.
        """
        with open(os.path.join(
                os.path.dirname(__file__), 'example.har.json')
        ) as example_file:
            self.example = json.load(example_file)
        self.entry = self.example["log"]["entries"][0]
        self.headers = test_har.array_to_dict(
                    self.entry["response"]["headers"])

    def test_success(self):
        """
        Test when the response matches all HAR values.
        """
        response = self.assertHAR(self.example)[0]

        self.assertEqual(
            response.status_code, self.entry["response"]["status"],
            'Wrong response status')
        self.assertEqual(
            response.reason, self.entry["response"]["statusText"],
            'Wrong response status text')
        self.assertEqual(
            response.headers['Content-Type'],
            self.entry["response"]["content"]["mimeType"],
            'Wrong response MIME type')

        response_headers = {
            key: value for key, value in response.headers.items()
            if key != 'Content-Type'}
        self.assertEqual(
            response_headers,
            test_har.array_to_dict(self.entry["response"]["headers"]),
            'Wrong response headers')

    def test_failure(self):
        """
        Test when the response fails to match.
        """
        # Capture the original values as what should be returned by the
        # backend/implementation being tested
        pass_entry = copy.deepcopy(self.entry)
        pass_headers = test_har.array_to_dict(
            pass_entry["response"]["headers"])

        # Moddify the HAR from which the assertions will be generated to
        # create assertion failures
        self.entry["response"]["status"] = 200
        self.entry["response"]["statusText"] = "OK"
        self.entry["response"]["headers"][0]["value"] = "foo"
        self.entry["response"]["headers"][1]["name"] = "Corge"
        self.entry["response"]["content"]["mimeType"] = "text/plain"
        self.entry["response"]["content"]["text"] = 'Foo plain text body'

        with self.assertRaises(AssertionError) as har_failures:
            self.assertHAR(self.example)

        self.assertIn(
            'response', dir(har_failures.exception),
            'Failure missing reference to the response')
        self.assertIsInstance(
            har_failures.exception.response, self.RESPONSE_TYPE,
            'Failure response is wrong type: {0}'.format(
                type(har_failures.exception.response)))

        # Confirm that the failures gathered are the same as the exceptions
        # would be raised if we'd specified them in the test.

        self.assertIn(
            'status', har_failures.exception.args[0],
            'Assertion exception missing status code detail')
        with self.assertRaises(AssertionError) as expected:
            self.assertEqual(
                pass_entry["response"]["status"],
                self.entry["response"]["status"],
                'Wrong response status code')
        self.assertEqual(
            har_failures.exception.args[0]['status'].args,
            expected.exception.args,
            'Wrong response status code failure assertion')

        self.assertIn(
            'statusText', har_failures.exception.args[0],
            'Assertion exception missing status text detail')
        with self.assertRaises(AssertionError) as expected:
            self.assertEqual(
                pass_entry["response"]["statusText"],
                self.entry["response"]["statusText"],
                'Wrong response status reason')
        self.assertEqual(
            har_failures.exception.args[0]['statusText'].args,
            expected.exception.args,
            'Wrong response status text failure assertion')

        self.assertIn(
            'content/mimeType', har_failures.exception.args[0],
            'Assertion exception missing MIME type detail')
        with self.assertRaises(AssertionError) as expected:
            self.assertEqual(
                pass_entry["response"]["content"]["mimeType"],
                self.entry["response"]["content"]["mimeType"],
                'Wrong response MIME type')
        self.assertEqual(
            har_failures.exception.args[0]['content/mimeType'].args,
            expected.exception.args,
            'Wrong response MIME type failure assertion')

        self.assertIn(
            'headers/Foo', har_failures.exception.args[0],
            'Assertion exception missing wrong header detail')
        with self.assertRaises(AssertionError) as expected:
            self.assertEqual(
                pass_headers["Foo"],
                self.entry["response"]["headers"][0]["value"],
                "Wrong response header {0!r} value: {1!r}".format(
                    'Foo', pass_headers["Foo"]))
        self.assertEqual(
            har_failures.exception.args[0]['headers/Foo'].args,
            expected.exception.args,
            'Wrong response header value failure assertion')

        self.assertIn(
            'headers/Corge', har_failures.exception.args[0],
            'Assertion exception missing absent header detail')
        with self.assertRaises(AssertionError) as expected:
            self.assertIn(
                'Corge', pass_headers,
                'Missing response header {0!r}'.format('Corge'))
        self.assertEqual(
            har_failures.exception.args[0]['headers/Corge'].args,
            expected.exception.args,
            'Wrong missing response header failure assertion')

        self.assertIn(
            'content/text', har_failures.exception.args[0],
            'Assertion exception missing wrong content text detail')
        with self.assertRaises(AssertionError) as expected:
            self.assertEqual(
                json.dumps(pass_entry["response"]["content"]["text"]),
                self.entry["response"]["content"]["text"],
                'Wrong response content text')
        self.assertEqual(
            har_failures.exception.args[0]['content/text'].args,
            expected.exception.args,
            'Wrong response content text failure assertion')

    def test_non_json(self):
        """
        Test when the response isn't JSON.
        """
        response = self.assertHAR(self.example)[0]
        self.assertEqual(
            response.text, self.entry["response"]["content"]["text"],
            'Wrong non-JSON response body')
