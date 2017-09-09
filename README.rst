============================================
test-har
============================================
Use HTTP Archive (HAR) files in Python tests
--------------------------------------------

To send this request to an API backend and assert the API response matches this
response...

.. code:: json

  {
    "log": {
      "version": "1.2",
      "entries": [
        {
          "request": {
            "method": "POST",
            "url": "mock://example.com/users/",
            "headers" : [
              {
                "name": "Accept",
                "value": "application/json"
              }
            ],
            "postData": {
              "mimeType": "application/json",
              "text" : {
                "username": "foo_username",
                "email": "foo@example.com",
                "group": "479e75e6-755a-46f1-a949-d6fee3671b3c"
              }
            },
            "comment" : "Test validation errors"
          },
          "response": {
            "status": 201,
            "statusText": "Created",
            "headers" : [
              {
                "name": "Allow",
                "value": "GET, POST, HEAD, OPTIONS"
              },
              {
                "name": "Vary",
                "value": "Accept, Cookie"
              }
            ],
            "content": {
              "mimeType": "application/json",
              "text": {
                "username": "foo_username"
              }
            }
          }
        }
      ]
    }
  }

Use this test:

.. code:: python

   import datetime

   # Import the appropriate backend for your framework.
   # Currently there are backends for the `requests` library...
   from test_har.requests_har as test_har
   # and for the Django ReST Framework.
   # from test_har.django_rest_har as test_har
   # Contributions for other frameworks welcome!
   
   from .. import models


   class MyAPITest(test_har.HARTestCase):
       """
       Specify the HAR file to use by default.
       """

       # Path to file relative to this test file
       # Set to `None` to skip automatic HAR parsing and set up
       example_har = 'example.har.json'
       
       def test_my_response(self):
           """
           Write your test as you would.
           """
           # For convenience, `self.example` is the parsed JSON in
           # `self.example_har`, `self.entry` is the first request/response
           # entry from `log/entries/0` in the HAR., `self.headers` is a
           # dictionary of the response headers for that entry, and
           # `self.content` is the response body content from that entry.

           # Make any changes to the test fixture necessary for the test such
           # as creating related objects before a POST that requires them.
           group = models.Group(
               name='foo_group',
               uuid=self.entry["request"]["postData"]["text"]["group"])

           # Make any changes to the HAR necessary for the assertions to work
           # before sending the requests
           self.content["some_dynamic_value"] = models.my_dynamic_function()

           # Send the HAR requests, assert responses match the HAR, and return
           # the responses.  Currently, assertions are made against the
           # response: `Status` code, `Status` reason text, `Content-Type`
           # MIME type, other headers in the HAR, and the response body
           # content.  If the response MIME type is a JSON type,
           # then assertions will be made against each top-level key
           # individually and ignore any key in the response not included in
           # the HAR.
           now = datetime.datetime.now()
           responses = self.assertHAR(self.example)

           # Make any other assertions, or do anything else you'd like to do,
           # with the responses.
           self.assertAlmostEqual(
               datetime.strptime(response[0].json()['created'], format='...'),
               now, delta=datetime.timedelta(seconds=1),
               msg='Wrong automatic creation time')

       def test_my_other_response(self):
           """
           Test a different HAR file.
           """
           # Replace `self.example` and the other convenience attributes with
           # the content form another HAR file
           self.setUpHAR('other.har.json')
           responses = self.assertHAR(self.example)
           ...

----
Why?
----

Writing tests for API backends can often involve a lot of repetitive code in
the tests to construct the content either to POST to the API or the expected
content in the response against which to make assertions.  For example,
constructing a Python dictionary to represent the JSON POSTed to or returned
from the API.  Similarly, testing the returned content often requires many
detailed assertions in order to sufficiently cover how the API should behave.

While writing this repetitive test code is tedious, more importantly, it isn't
very readable and makes discerning the intended behavior the test is meant to
cover unnecessarily difficult.  Ideally, one should be able to describe the
expected behavior of the API in a format much closer to the format used by the
API.  Also ideally, one should be able to clearly read related requests and
responses together.

The JSON-based `HTTP Archive`_ (HAR) format used by browsers for recording
browser sessions gives us exactly such a format, especially for JSON-based
APIs.  The `test_har` package provides support for using HAR files to drive
tests and make the more common assertions against the response while still
allowing the developer to continue doing anything not able to be covered using
the HAR file the same way they would have otherwise.


.. _HTTP Archive: https://dvcs.w3.org/hg/webperf/raw-file/tip/specs/HAR/Overview.html
