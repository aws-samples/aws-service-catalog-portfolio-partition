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


class S3Bucket(Base):

    def _arn(self):
        bucket_name = self.physical_id.split(':')[-1]
        return 'arn:aws:s3:::{}'.format(bucket_name)

    def _service_name(self):
        return 's3'

    def _access_to(self):
        return True

    def _access_from(self):
        return False

    def _assumed_role(self):
        return None

    def _trust_relationship_service(self):
        return "s3.amazonaws.com"

    def _statement_id(self):
        return "DedicatedForResourceTypeS3"

    def _actions(self):
        return "*"
