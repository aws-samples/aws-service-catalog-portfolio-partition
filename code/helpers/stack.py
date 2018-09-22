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
from helpers.utils.session import Session
from helpers.exceptions import TagNotExist

NOT_APPLICABLE_RESOURCE_STATUS = ('DELETE_COMPLETE', 'CREATE_FAILED')
APPLICABLE_RESOURCE_STATUS = ('CREATE_COMPLETE', 'DELETE_FAILED', 'UPDATE_COMPLETE')


class Stack(object):

    def __init__(self, stack_id):
        self.session = Session()
        self.arn = stack_id
        cfn_resource = self.session.resource('cloudformation')
        self.aro = cfn_resource.Stack(self.arn)

    def tag(self, key, exception=False):
        value = jmespath.search(
            "[?Key=='{}'].Value|[0]".format(key),
            self.aro.tags
        )
        if not value:
            if exception:
                raise TagNotExist(key)
        return value

    def stack_resources(self):
        resources = []
        for resource in self.aro.resource_summaries.all():
            stack_resource = self.aro.Resource(resource.logical_id)
            if stack_resource.resource_status not in NOT_APPLICABLE_RESOURCE_STATUS:
                resources.append(stack_resource)
        return resources

    # TODO conclude the new created and the deleted and the replaced resources
    def stack_resources_change(self):
        resources = []
        for resource in self.aro.resource_summaries.all():
            resource_obj = self.aro.Resource(resource.logical_id)
            resources.append(resource_obj)
        return resources
