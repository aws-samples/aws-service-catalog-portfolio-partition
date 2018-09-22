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
import re
from pathlib import Path
from helpers.resources.factory import Factory
from helpers.defaults import APPLICABLE_FILE, ACTIONS_FILE
from helpers.defaults import ALLOWED_ACTIONS
from helpers.exceptions import InvalidConfiguration


class ResourcesGenerator(object):

    def __init__(
        self,
        stack_resources,
        resources_fp=APPLICABLE_FILE,
        actions_fp=ACTIONS_FILE
    ):
        self.file_applicable = Path(resources_fp).resolve().as_posix()
        self._applicable = None
        self.file_allowed_actions = Path(actions_fp).resolve().as_posix()
        self._actions = None
        self.stack_resources = stack_resources

    @property
    def applicability(self):
        if not self._applicable:
            with open(self.file_applicable, 'r') as stream:
                self._applicable = json.loads(stream.read())
        return self._applicable

    @property
    def actions(self):
        if not self._actions:
            with open(self.file_allowed_actions, 'r') as stream:
                self._actions = json.loads(stream.read())
        return self._actions

    def applicable(self, resource_type):
        if resource_type in self.applicability['Applicable']:
            return True
        for non_applicable_rtype in self.applicability['NotApplicable']:
            if re.search(
                non_applicable_rtype,
                resource_type,
                flags=re.IGNORECASE
            ):
                return False

    def validate_configuration(self):
        missing_types = []
        for stack_resource in self.stack_resources:
            if self.applicable(stack_resource.resource_type) in (True, False):
                continue
            else:
                missing_types.append(stack_resource.resource_type)
        if missing_types:
            print('missing types : {}'.format(missing_types))
            raise InvalidConfiguration(missing_types)

    def allowed_actions(self, resource_type):
        return self.actions.get(resource_type, ALLOWED_ACTIONS)

    def generator(self):
        for stack_resource in self.stack_resources:
            if not self.applicable(stack_resource.resource_type):
                continue
            resource = Factory(
                stack_resource.resource_type,
                stack_resource.physical_resource_id,
                actions=self.allowed_actions(stack_resource.resource_type)
            )
            if not resource:
                continue
            yield resource
