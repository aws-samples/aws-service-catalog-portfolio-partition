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

from boto3.exceptions import ResourceNotExistsError
from helpers.utils.catch_error import catch_error
from helpers.utils.session import Session
from helpers.utils import convertor


class Base(object):

    def __init__(self, physical_id, **kwargs):
        self.physical_id = physical_id

        self._session = Session()
        self._client = self._session.client(self._service_name())
        self._resource = self._resource()
        self._iam_client = self._session.client('iam')
        self._iam_resource = self._session.resource('iam')

        self.arn = self._arn()
        self.service_name = self._service_name()
        self.access_to = self._access_to()
        self.access_from = self._access_from()
        self.assumed_role = self._assumed_role()
        self.trust_relationship_service = self._trust_relationship_service()
        self.statement_id = self._statement_id()
        self.actions = kwargs.get('actions', self._actions())

    def __str__(self):
        return "Resource id: {} Arn: {}".format(self.physical_id, self.arn)

    @catch_error(ResourceNotExistsError)
    def _resource(self):
        return self._session.resource(self._service_name())

    def _arn(self):
        return None

    def _service_name(self):
        return None

    def _access_to(self):
        return False

    def _access_from(self):
        return False

    def _assumed_role(self):
        return None

    def _trust_relationship_service(self):
        return None

    def _statement_id(self):
        return None

    def _actions(self):
        return None

    def attach_policy(self, policy):
        if not self.assumed_role:
            return
        role_name = convertor.arn_to_name(self.assumed_role)
        self._iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy
        )

    def assume_role(self, role):
        pass

    def detach_policy(self, policy):
        if not self.assumed_role:
            return
        role_name = convertor.arn_to_name(self.assumed_role)
        self._iam_client.detach_role_policy(
            RoleName=role_name,
            PolicyArn=policy
        )

    def stop_assume_role(self, role):
        pass
