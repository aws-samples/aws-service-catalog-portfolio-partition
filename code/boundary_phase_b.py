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
import json
from boto3.dynamodb.conditions import Attr

from helpers.utils.session import Session
from helpers.logger import logger
from helpers.defaults import BASE_POLICY
from helpers.exceptions import EventParsingError
from helpers.controllers.policy import Policy
from helpers.controllers.role import Role
from helpers.utils import convertor

session = Session()
dynamodb_resource = session.resource('dynamodb')


def handler(event, context):
    logger.debug(event)

    table_arn = jmespath.search(
        "Records[?eventSource=='aws:dynamodb'].eventSourceARN | [0]",
        event
    ).split('/stream/')[0]
    if not table_arn:
        raise(EventParsingError('eventSourceARN'))
    table = dynamodb_resource.Table(convertor.arn_to_name(table_arn))

    altered_policies = jmespath.search(
        "Records[?eventSource=='aws:dynamodb'].dynamodb.Keys.policy.S",
        event
    )
    # TODO handle scan api call limit
    for policy in altered_policies:
        items = table.scan(FilterExpression=Attr('policy').eq(policy))['Items']
        policy_resource = Policy(policy)
        if not items:
            policy_resource.delete()
            Role(policy.replace('policy', 'role')).delete()
        else:
            policy_document = table_items_to_document(items)
            policy_resource.update_document(policy_document)


def table_items_to_document(items):
    statements = []
    sids = set(jmespath.search("[].sid", items))
    for sid in sids:
        actions = list(
            set(
                jmespath.search(
                    "[?sid=='{}'].actions | [][]".format(sid),
                    items
                )
            )
        )
        resources = jmespath.search("[?sid=='{}'].arn".format(sid), items)
        statements.append(
            {
                'Sid': sid,
                'Resource': resources,
                'Action': actions,
                'Effect': 'Allow'
            }
        )
    if statements:
        return {
            "Version": "2012-10-17",
            "Statement": statements
        }
    else:
        return json.loads(BASE_POLICY)
