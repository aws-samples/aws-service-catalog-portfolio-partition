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

from helpers.utils.session import Session


class Table():
    def __init__(self, name):
        self.session = Session()
        self.dynamodb_client = self.session.client('dynamodb')
        self.dynamodb_resource = self.session.resource('dynamodb')
        self.name = name
        self.aro = self.dynamodb_resource.Table(self.name)

    def add(self, items):
        with self.aro.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)

    def remove(self, items):
        with self.aro.batch_writer() as batch:
            for item in items:
                print('item: {}'.format(item))
                batch.delete_item(Key=item)
