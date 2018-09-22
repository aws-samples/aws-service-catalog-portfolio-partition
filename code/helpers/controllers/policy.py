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


class Policy(object):

    def __init__(self, arn):
        self.session = Session()
        self.iam_client = self.session.client('iam')
        self.iam_resource = self.session.resource('iam')
        self.arn = arn
        self.name = arn_to_name(self.arn)
        self.aro = self.iam_resource.Policy(self.arn)

    def delete_non_default_versions(self):
        for policy_version in self.aro.versions.all():
            if not policy_version.is_default_version:
                policy_version.delete()

    def detach_roles(self):
        for rol in self.aro.attached_roles.all():
            rol.detach_policy(PolicyArn=self.arn)

    @client_error_retry('LimitExceeded', delete_non_default_versions)
    def update_document(self, document):
        self.iam_client.create_policy_version(
            PolicyArn=self.arn,
            PolicyDocument=json.dumps(document),
            SetAsDefault=True
        )
        logger.info('Policy document updated: {}'.format(document))

    @client_error_retry('DeleteConflict', detach_roles)
    @client_error_retry('DeleteConflict', delete_non_default_versions)
    def delete(self):
        self.aro.delete()
