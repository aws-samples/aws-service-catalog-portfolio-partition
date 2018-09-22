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

import jmespath
from botocore.exceptions import ClientError
from helpers.logger import logger
from helpers.utils.session import Session


class Policies(object):

    def __init__(self):
        self.session = Session()
        self.iam_client = self.session.client('iam')
        self.iam_resource = self.session.resource('iam')

    def find(self, path, name):
        paginator = self.iam_client.get_paginator('list_policies')
        response_iterator = paginator.paginate(
            Scope='Local',
            OnlyAttached=False,
            PathPrefix='/{}/'.format(path),
            PaginationConfig={
                'MaxItems': 123,
                'PageSize': 123
            }
        )
        result = []
        for response in response_iterator:
            result += jmespath.search(
                "Policies[?PolicyName=='{}'].Arn".format(name),
                response
            )
        return jmespath.search("[0]", result)

    def create(self, path, name, base_policy):
        try:
            response = self.iam_client.create_policy(
                Path='/{}/'.format(path),
                PolicyName=name,
                PolicyDocument=base_policy,
                Description='Set the access to resources provisioned by products \
                associated with Service Catalog Portfolio {}'.format(name)
            )
            logger.info('Policy created: {}'.format(name))
            return response['Policy']['Arn']
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                return self.find(path, name)
