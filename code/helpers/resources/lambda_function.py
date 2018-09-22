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

from helpers.resources.base import Base
from botocore.exceptions import ClientError
from helpers.exceptions import MissingTrustRelationshipError


class LambdaFunction(Base):

    def _arn(self):
        return self._client.get_function(
            FunctionName=self.physical_id
        )['Configuration']['FunctionArn']

    def _service_name(self):
        return 'lambda'

    def _access_to(self):
        return True

    def _access_from(self):
        return True

    def _assumed_role(self):
        if not self.arn:
            return None
        role = self._client.get_function_configuration(
            FunctionName=self.arn
        ).get('Role', None)
        if role == '':
            return None
        return role.split('role/')[-1]

    def _trust_relationship_service(self):
        return "lambda.amazonaws.com"

    def _statement_id(self):
        return "DedicatedForResourceTypeLambda"

    def _actions(self):
        return "*"

    def assume_role(self, role):
        if not self.arn:
            return None
        try:
            self._client.update_function_configuration(
                FunctionName=self.arn,
                Role=role
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidParameterValueException':
                if e.response['Error']['Message'] == '\
                        The role defined for the function cannot be assumed\
                        by Lambda.':
                    raise MissingTrustRelationshipError()

    def stop_assume_role(self, role):
        pass
