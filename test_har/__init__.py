import re
import collections
import unittest


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

            try:
                self.assertEqual(
                    response.status_code, entry["response"]["status"],
                    'Wrong response status code')
            except AssertionError as exc:
                failures['status'] = exc

            try:
                self.assertEqual(
                    reason, entry["response"]["statusText"],
                    'Wrong response status reason')
            except AssertionError as exc:
                failures['statusText'] = exc

            content_type = entry["response"]["content"].get("mimeType")
            if content_type:
                try:
                    self.assertIn(
                        'Content-Type', response_headers,
                        'Response missing MIME type')
                    self.assertEqual(
                        response_headers['Content-Type'],
                        entry["response"]["content"]["mimeType"],
                        'Wrong response MIME type')
                except AssertionError as exc:
                    failures['content/mimeType'] = exc

            for header in entry["response"].get("headers", []):
                try:
                    self.assertIn(
                        header['name'], response_headers,
                        'Missing response header {0!r}'.format(
                            header['name']))
                    self.assertEqual(
                        response_headers[header['name']], header['value'],
                        'Wrong response header {0!r} value: {1!r}'.format(
                            header['name'], response_headers[header['name']]))
                except AssertionError as exc:
                    failures['headers/{0}'.format(header['name'])] = exc

            try:
                if (
                        self.JSON_MIME_TYPE_RE.match(
                            response_headers['Content-Type']) is not None and
                        not isinstance(
                            entry["response"]["content"]["text"], str)):
                    # Support including JSON in the HAR content text
                    content = response.json()
                else:
                    content = text

                self.assertEqual(
                    content, entry["response"]["content"]["text"],
                    'Wrong response content text')
            except AssertionError as exc:
                failures['content/text'] = exc

            if failures:
                raise HAREntryAssertionError(response, failures)

        return responses
