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
import jmespath
from helpers.logger import logger
from helpers.utils.session import Session
from helpers.utils.catch_error import client_error_retry
from helpers.utils.convertor import arn_to_name

'''
Limits:
    Managed policies attached to an IAM role 10
    Roles in an instance profile 1
    Versions of a managed policy that can be stored 5
    Role trust policy JSON text  2,048 characters
    Role inline policy size cannot exceed 10,240 characters
        (exclude whitespaces)
    The size of each managed policy cannot exceed 6,144 characters
        (exclude whitespaces)
'''


class Role(object):

    def __init__(self, arn):
        self.session = Session()
        self.iam_client = self.session.client('iam')
        self.iam_resource = self.session.resource('iam')
        self.arn = arn
        self.name = arn_to_name(self.arn)
        self.aro = self.iam_resource.Role(self.name)

    def attach_policy(self, policy_arn):
        self.aro.attach_policy(PolicyArn=policy_arn)

    def update_trust_document(self, service_name):
        policy = self.aro.AssumeRolePolicy()
        policy_doc = self.aro.assume_role_policy_document
        principal_service = jmespath.search(
            "Statement[].Principal.Service", policy_doc
        )
        principal_service = jmespath.search("[][][]", principal_service)
        if service_name not in principal_service:
            principal_service.append(service_name)
        policy_doc['Statement'] = [
            {'Action': 'sts:AssumeRole',
             'Effect': 'Allow',
             'Principal': {'Service': principal_service}}
        ]
        policy.update(PolicyDocument=json.dumps(policy_doc))
        logger.debug("Trust policy updated: {}".format(policy_doc))

    def _stop_being_assumed(self):
        pass

    def _detach_policy(self):
        pass

    # TODO implement the resolver methods
    @client_error_retry('DeleteConflict', _stop_being_assumed)
    @client_error_retry('DeleteConflict', _detach_policy)
    def delete(self):
        self.aro.delete()
