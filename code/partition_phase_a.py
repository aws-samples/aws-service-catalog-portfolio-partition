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

import os
from helpers import custom_resource_handler
from helpers.stack import Stack
from helpers.partition import Partition
from helpers.resources_generator import ResourcesGenerator
from helpers.defaults import PORTFOLIO_ID_TAG

TABLE = os.environ['IAM_POLICY_TABLE']

handler = custom_resource_handler.Resource()


@handler.create
def add(event, context):
    stack = Stack(event['StackId'])
    portfolio_arn = stack.tag(PORTFOLIO_ID_TAG, exception=True)
    portfolio_id = portfolio_arn.split('/')[-1]

    partition = Partition(portfolio_id, TABLE)
    resources_generator = ResourcesGenerator(stack.stack_resources()).generator()
    partition.include(resources_generator)

    return {}


# TODO update policy according to resources status
@handler.update
def modify(event, context):
    stack = Stack(event['StackId'])
    portfolio_arn = stack.tag(PORTFOLIO_ID_TAG, exception=True)
    portfolio_id = portfolio_arn.split('/')[-1]

    partition = Partition(portfolio_id, TABLE)
    resources_generator = ResourcesGenerator(stack.stack_resources()).generator()
    partition.include(resources_generator)
    partition.exclude(resources_generator)

    return {}


@handler.delete
def remove(event, context):
    stack = Stack(event['StackId'])
    portfolio_arn = stack.tag(PORTFOLIO_ID_TAG, exception=True)
    portfolio_id = portfolio_arn.split('/')[-1]

    partition = Partition(portfolio_id, TABLE)
    resources_generator = ResourcesGenerator(stack.stack_resources()).generator()
    partition.exclude(resources_generator)

    return {}
