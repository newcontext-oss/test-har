import re
import unittest


JSON_MIME_TYPE_RE = re.compile(r'application/([^/+]+\+)?json')


def array_to_dict(array, key='name', value='value'):
    """
    Convert an array of name/value objects to a dict.
    """
    return {item[key]: item[value] for item in array}


class HARTestCase(unittest.TestCase):
    """
    Run tests using HTTP Archive (HAR) files.
    """

    JSON_MIME_TYPE_RE = JSON_MIME_TYPE_RE

    def assertHAR(self, har):
        """
        Send requests in the HAR and make assertions on the HAR responses.
        """
        responses = []
        failures = {}
        for entry in har["log"]["entries"]:
            headers = array_to_dict(entry["request"].get("headers", []))

            response = self._request_har(
                method=entry["request"]["method"],
                url=entry["request"]["url"], headers=headers)

            try:
                self.assertEqual(
                    response.status_code, entry["response"]["status"],
                    'Wrong response status code')
            except AssertionError as exc:
                failures['status'] = exc

            try:
                self.assertEqual(
                    response.reason, entry["response"]["statusText"],
                    'Wrong response status reason')
            except AssertionError as exc:
                failures['statusText'] = exc

            content_type = entry["response"]["content"].get("mimeType")
            if content_type:
                try:
                    self.assertIn(
                        'Content-Type', response.headers,
                        'Response missing MIME type')
                    self.assertEqual(
                        response.headers['Content-Type'],
                        entry["response"]["content"]["mimeType"],
                        'Wrong response MIME type')
                except AssertionError as exc:
                    failures['content/mimeType'] = exc

            response_headers = dict(response.headers)
            response_headers.pop('Content-Type', None)
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
                            response.headers['Content-Type']) is not None and
                        not isinstance(
                            entry["response"]["content"]["text"], str)):
                    # Support including JSON in the HAR content text
                    content = response.json()
                else:
                    content = response.text

                self.assertEqual(
                    content, entry["response"]["content"]["text"],
                    'Wrong response content text')
            except AssertionError as exc:
                failures['content/text'] = exc

            responses.append(response)

        if failures:
            self.fail(failures)

        return responses
