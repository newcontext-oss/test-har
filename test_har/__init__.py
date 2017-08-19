import os
import re
import collections
import json
import inspect
import unittest

try:
    import collections.abc as collections_abc
except ImportError:  # pragma: no cover
    # BBB Python 2 compat
    import collections as collections_abc  # noqa


JSON_MIME_TYPE_RE = re.compile(r'application/([^/+]+\+)?json')


def array_to_dict(array, key='name', value='value'):
    """
    Convert an array of name/value objects to a dict.
    """
    return {item[key]: item[value] for item in array}


class HAREntryAssertionError(AssertionError):
    """
    Collect multiple failures for a single entries response.
    """

    def __init__(self, response, *args):
        """
        Record the response corresponding to the failures.
        """
        self.response = response
        super(HAREntryAssertionError, self).__init__(*args)


class HARTestCase(unittest.TestCase):
    """
    Run tests using HTTP Archive (HAR) files.
    """

    JSON_MIME_TYPE_RE = JSON_MIME_TYPE_RE

    example_har = None

    def setUp(self):
        """
        Load an example HAR file.
        """
        super(HARTestCase, self).setUp()

        if self.example_har is not None:
            self.setUpHAR(self.example_har)

    def setUpHAR(self, example_har):
        """
        Load an example HAR file.
        """
        with open(os.path.join(
                os.path.dirname(inspect.getfile(type(self))),
                example_har)
        ) as example_file:
            self.example = json.load(example_file)
        self.entry = self.example["log"]["entries"][0]
        self.headers = array_to_dict(
            self.entry["response"].get("headers", []))
        self.content = self.entry["response"]["content"]["text"]

    def get_reason(self, response):
        """
        Lookup the implementation-specific response reason phrase.
        """
        raise NotImplementedError(  # pragma: no cover
            'Subclasses must override `get_reason`')

    def get_headers(self, req_or_resp):
        """
        Lookup the implementation-specific headers on a request or response.
        """
        raise NotImplementedError(  # pragma: no cover
            'Subclasses must override `get_headers`')

    def get_text(self, response):
        """
        Lookup the implementation-specific response body text.
        """
        raise NotImplementedError(  # pragma: no cover
            'Subclasses must override `get_text`')

    def assertHAR(self, har):
        """
        Send requests in the HAR and make assertions on the HAR responses.
        """
        responses = []
        for entry in har["log"]["entries"]:
            headers = array_to_dict(entry["request"].get("headers", []))
            request = dict(
                method=entry["request"]["method"],
                url=entry["request"]["url"],
                headers=headers)

            post = entry["request"].get('postData')
            if post is not None:
                headers['Content-Type'] = post["mimeType"]
                request['data'] = post["text"]

            response = self.request_har(**request)
            responses.append(response)
            failures = collections.OrderedDict()

            reason = self.get_reason(response)
            response_headers = self.get_headers(response)
            text = self.get_text(response)

            response_status = response.status_code
            expected_status = entry["response"]["status"]
            try:
                self.assertEqual(
                    response_status, expected_status,
                    'Wrong response status code')
            except AssertionError as exc:
                failures['status'] = exc

            # BBB Python 2.7 str vs unicode compat
            expected_reason = type(reason)(entry["response"]["statusText"])
            try:
                self.assertEqual(
                    reason,
                    expected_reason,
                    'Wrong response status reason')
            except AssertionError as exc:
                failures['statusText'] = exc

            content_type = entry["response"]["content"].get("mimeType")
            if content_type:
                try:
                    self.assertIn(
                        'Content-Type', response_headers,
                        'Missing response content type')
                except AssertionError as exc:
                    failures['content/mimeType'] = exc
                else:
                    expected_content_type = type(
                        response_headers['Content-Type'])(
                            entry["response"]["content"]["mimeType"])
                    try:
                        self.assertEqual(
                            response_headers['Content-Type'],
                            # BBB Python 2.7 str vs unicode compat
                            expected_content_type,
                            'Wrong response MIME type')
                    except AssertionError as exc:
                        failures['content/mimeType'] = exc

            for header in entry["response"].get("headers", []):
                header_name = header['name']
                # BBB Python 2.7 str vs unicode compat
                try:
                    self.assertIn(
                        header_name, response_headers,
                        'Missing response header')
                except AssertionError as exc:
                    failures['headers/{0}'.format(header_name)] = exc
                else:
                    expected_header_value = type(
                        response_headers[header_name])(header['value'])
                    try:
                        self.assertEqual(
                            response_headers[header_name],
                            expected_header_value,
                            'Wrong response header {0!r} value'.format(
                                header_name))
                    except AssertionError as exc:
                        failures['headers/{0}'.format(header_name)] = exc

            expected_content = entry["response"]["content"]["text"]
            if self.JSON_MIME_TYPE_RE.match(
                    response_headers.get('Content-Type', '')) is not None:
                # Support including JSON in the HAR content text
                content = response.json()
                if (
                        isinstance(content, collections_abc.Mapping) and
                        isinstance(expected_content, collections_abc.Mapping)):
                    for key, value in expected_content.items():
                        try:
                            self.assertIn(key, content, 'Missing content key')
                        except AssertionError as exc:
                            failures['content/{0}'.format(key)] = exc
                        else:
                            try:
                                self.assertEqual(
                                    content[key], value,
                                    'Wrong content {0!r} value'.format(key))
                            except AssertionError as exc:
                                failures['content/{0}'.format(key)] = exc
                else:
                    try:
                        self.assertEqual(
                            content, expected_content,
                            'Mismatched response content type')
                    except AssertionError as exc:
                        failures['content/text'] = exc
            else:
                try:
                    self.assertEqual(
                        text, expected_content,
                        'Wrong response content text')
                except AssertionError as exc:
                    failures['content/text'] = exc

            if failures:
                raise HAREntryAssertionError(response, failures)

        return responses
