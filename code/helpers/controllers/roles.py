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

from helpers.logger import logger
from helpers.utils.session import Session
from helpers.utils.catch_error import client_error_ignore


class Roles(object):

    def __init__(self):
        self.session = Session()
        self.iam_client = self.session.client('iam')
        self.iam_resource = self.session.resource('iam')

    @client_error_ignore('NoSuchEntity')
    def find(self, name):
        aro = self.iam_resource.Role(name)
        aro.create_date
        return aro.arn

    def create(self, path, name, base_trust_policy):
        response = self.iam_client.create_role(
            Path='/{}/'.format(path),
            RoleName=name,
            AssumeRolePolicyDocument=base_trust_policy,
            Description='Assumed by resources provisioned by products \
             associated with Service Catalog Portfolio {}'.format(name)
        )
        logger.debug('Role created: {}'.format(name))
        return response['Role']['Arn']
