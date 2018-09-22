'''
 Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 Permission is hereby granted, free of charge, to any person obtaining a copy of this
 software and associated documentation files (the "Software"), to deal in the Software
 without restriction, including without limitation the rights to use, copy, modify,
 merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
 permit persons to whom the Software is furnished to do so.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
 PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import json
from botocore.vendored import requests
from helpers.logger import logger

SUCCESS = 'SUCCESS'
FAILED = 'FAILED'


def wrap_user_handler(func, base_response=None):
    def wrapper_func(event, context):

        logger.debug(
            "Received %s request with event: %s" % (
                event['RequestType'], json.dumps(event)
            )
        )

        response = {
            "StackId": event["StackId"],
            "RequestId": event["RequestId"],
            "LogicalResourceId": event["LogicalResourceId"],
            "PhysicalResourceId": "custom_resource_physical_id",
            "Status": SUCCESS,
        }
        if event.get("PhysicalResourceId", False):
            response["PhysicalResourceId"] = event["PhysicalResourceId"]

        if base_response is not None:
            response.update(base_response)

        try:
            response.update(func(event, context))
        except NoResponse:
            # Do nothing, maybe we're being rescheduled?
            return
        except Exception as e:
            logger.exception("Failed to execute resource function")
            reason = "Exception was raised while handling custom resource."
            reason += " Message {}".format(e.args or e.message)
            response.update({
                "Status": FAILED,
                "Reason": reason,
                "Data": {'FailureReason': reason}
            })

        serialized = json.dumps(response)
        logger.info("Responding to '%s' request with: %s" % (
            event['RequestType'], serialized))

        req = requests.put(
            event['ResponseURL'], data=serialized,
            headers={'Content-Length': str(len(serialized)),
                     'Content-Type': ''}
        )

        try:
            req
            logger.debug("Request to CFN API succeeded, nothing to do here")
        except requests.HTTPError as e:
            logger.error("Callback to CFN API failed with status %d" % e.code)
            logger.error("Response: %s" % e.reason)
        except requests.ConnectionError as e:
            logger.error("Failed to reach the server - %s" % e.reason)

    return wrapper_func


class Resource(object):
    _dispatch = None

    def __init__(self, wrapper=wrap_user_handler):
        self._dispatch = {}
        self._wrapper = wrapper

    def __call__(self, event, context):
        request = event['RequestType']
        logger.debug("Received {} type event. Full parameters: {}".format(request, json.dumps(event)))
        return self._dispatch.get(request, self._succeed())(event, context)

    def _succeed(self):
        @self._wrapper
        def success(event, context):
            return {
                'Status': SUCCESS,
                'PhysicalResourceId': event.get('PhysicalResourceId', 'none-physical-resource-id'),
                'Reason': 'Request type {} is unknown'.format(event['RequestType']),
                'Data': {}
            }
        return success

    def create(self, wraps):
        self._dispatch['Create'] = self._wrapper(wraps)
        return wraps

    def update(self, wraps):
        self._dispatch['Update'] = self._wrapper(wraps)
        return wraps

    def delete(self, wraps):
        self._dispatch['Delete'] = self._wrapper(wraps)
        return wraps


class NoResponse(Exception):
    pass
