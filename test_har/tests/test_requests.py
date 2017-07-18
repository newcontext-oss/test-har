"""
Test using HAR files in Python tests against the requests library.
"""

from __future__ import unicode_literals

import os
import json

import requests_mock

from test_har import requests_har as test_har


@requests_mock.Mocker()
class HARDogfoodRequestsTests(test_har.HARTestCase):
    """
    Test using HAR files in Python tests against the requests library.
    """

    def test_runner(self, mocker):
        """
        Ensure tests are running.
        """
        self.assertTrue(True)

    def test_success(self, mocker):
        """
        Test when the response matches all HAR values.
        """
        with open(os.path.join(
                os.path.dirname(__file__), 'example.har.json')
        ) as example_file:
            example = json.load(example_file)

        entry = example["log"]["entries"][0]

        headers = {
            header["name"]: header["value"]
            for header in entry["response"]["headers"]}
        headers['Content-Type'] = 'application/json'

        mocker.post(
            entry["request"]["url"], status_code=entry["response"]["status"],
            reason=entry["response"]["statusText"], headers=headers,
            text=json.dumps(entry["response"]["content"]["text"]))
        response = self.assertHAR(example)[0]

        response_headers = {
            key: value for key, value in response.headers.items()
            if key != 'Content-Type'}
        self.assertEqual(
            response_headers,
            test_har.array_to_dict(entry["response"]["headers"]),
            'Wrong response headers')

        self.assertEqual(
            response.status_code, entry["response"]["status"],
            'Wrong response status')
        self.assertEqual(
            response.reason, entry["response"]["statusText"],
            'Wrong response status text')
        self.assertEqual(
            response.headers['Content-Type'],
            entry["response"]["content"]["mimeType"],
            'Wrong response MIME type')
        self.assertEqual(
            {key: value for key, value in response.headers.items()
             if key != 'Content-Type'},
            test_har.array_to_dict(entry["response"]["headers"]),
            'Wrong response headers')

    def test_failure(self, mocker):
        """
        Test when the response fails to match.
        """
        with open(os.path.join(
                os.path.dirname(__file__), 'example.har.json')
        ) as example_file:
            example = json.load(example_file)
        entry = example["log"]["entries"][0]
        entry["response"]["status"] = 200
        entry["response"]["statusText"] = "OK"
        entry["response"]["content"]["mimeType"] = "text/plain"

        headers = {"Content-Type": "application/json", "Foo": "foo"}
        response_kwargs = dict(
            status_code=400, reason='Invalid', headers=headers,
            text=json.dumps({"error": "Too short"}))
        mocker.post(entry["request"]["url"], **response_kwargs)
        with self.assertRaises(AssertionError) as cm:
            self.assertHAR(example)

        # Confirm that the failures gathered are the same as the exceptions
        # would be raised if we'd specified them in the test.

        self.assertIn(
            'status', cm.exception.args[0],
            'Assertion exception missing status code detail')
        try:
            self.assertEqual(
                response_kwargs['status_code'], entry["response"]["status"],
                'Wrong response status code')
        except AssertionError as exc:
            self.assertEqual(
                cm.exception.args[0]['status'].args, exc.args,
                'Wrong response status code failure assertion')

        self.assertIn(
            'statusText', cm.exception.args[0],
            'Assertion exception missing status text detail')
        try:
            self.assertEqual(
                response_kwargs['reason'], entry["response"]["statusText"],
                'Wrong response status reason')
        except AssertionError as exc:
            self.assertEqual(
                cm.exception.args[0]['statusText'].args, exc.args,
                'Wrong response status text failure assertion')

        self.assertIn(
            'content/mimeType', cm.exception.args[0],
            'Assertion exception missing MIME type detail')
        try:
            self.assertEqual(
                response_kwargs['headers']['Content-Type'],
                entry["response"]["content"]["mimeType"],
                'Wrong response MIME type')
        except AssertionError as exc:
            self.assertEqual(
                cm.exception.args[0]['content/mimeType'].args, exc.args,
                'Wrong response MIME type failure assertion')

        self.assertIn(
            'headers/Foo', cm.exception.args[0],
            'Assertion exception missing wrong header detail')
        try:
            self.assertEqual(
                response_kwargs['headers']['Foo'],
                test_har.array_to_dict(entry["response"]["headers"])["Foo"],
                'Wrong response header {0!r} value: {1!r}'.format(
                    'Foo', response_kwargs['headers']['Foo']))
        except AssertionError as exc:
            self.assertEqual(
                cm.exception.args[0]['headers/Foo'].args, exc.args,
                'Wrong response header value failure assertion')

        self.assertIn(
            'headers/Qux', cm.exception.args[0],
            'Assertion exception missing absent header detail')
        try:
            self.assertIn(
                'Qux', response_kwargs['headers'],
                'Missing response header {0!r}'.format('Qux'))
        except AssertionError as exc:
            self.assertEqual(
                cm.exception.args[0]['headers/Qux'].args, exc.args,
                'Missing response header failure assertion')

        self.assertIn(
            'content/text', cm.exception.args[0],
            'Assertion exception missing wrong content text detail')
        try:
            self.assertEqual(
                json.loads(response_kwargs['text']),
                entry["response"]["content"]["text"],
                'Wrong response content text')
        except AssertionError as exc:
            self.assertEqual(
                cm.exception.args[0]['content/text'].args, exc.args,
                'Wrong response content text failure assertion')

    def test_non_json(self, mocker):
        """
        Test when the response isn't JSON.
        """
        with open(os.path.join(
                os.path.dirname(__file__), 'example.har.json')
        ) as example_file:
            example = json.load(example_file)
        entry = example["log"]["entries"][0]
        entry["response"]["content"]["mimeType"] = "text/plain"
        entry["response"]["content"]["text"] = 'Foo plain text body'

        headers = {
            header["name"]: header["value"]
            for header in entry["response"]["headers"]}
        headers["Content-Type"] = entry["response"]["content"]["mimeType"]

        mocker.post(
            entry["request"]["url"], status_code=entry["response"]["status"],
            reason=entry["response"]["statusText"], headers=headers,
            text=entry["response"]["content"]["text"])
        response = self.assertHAR(example)[0]
        self.assertEqual(
            response.text, entry["response"]["content"]["text"],
            'Wrong non-JSON response body')
