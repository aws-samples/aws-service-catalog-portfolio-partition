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

from helpers.exceptions import MissingTrustRelationshipError
from helpers.logger import logger
from helpers.controllers.policies import Policies
from helpers.controllers.policy import Policy
from helpers.controllers.roles import Roles
from helpers.controllers.role import Role
from helpers.controllers.table import Table
from helpers.defaults import BASE_POLICY
from helpers.defaults import BASE_TRUST_POLICY


class Boundary(object):

    def __init__(self, portfolio_id, table_name):
        self.table = Table(table_name)
        self.policies = Policies()
        policy_arn = self.policies.find(portfolio_id, portfolio_id) \
            or self.policies.create(portfolio_id, portfolio_id, BASE_POLICY)
        self.policy = Policy(policy_arn)
        self.roles = Roles()
        role_arn = self.roles.find(portfolio_id) \
            or self.roles.create(portfolio_id, portfolio_id, BASE_TRUST_POLICY)
        self.role = Role(role_arn)
        self.role.attach_policy(self.policy.arn)

    def include(self, resource_generator):
        items = []
        for resource in resource_generator:
            logger.debug('include resource {}'.format(resource.arn))
            if resource.access_to:
                items.append({
                    'arn': resource.arn,
                    'policy': self.policy.arn,
                    'sid': resource.statement_id,
                    'actions': resource.actions
                })
                if resource.assumed_role:
                    resource.attach_policy(self.policy.arn)
            if resource.access_from and not resource.assumed_role:
                try:
                    resource.assume_role(self.role.arn)
                except MissingTrustRelationshipError:
                    self.role.update_trust_document(
                        resource.trust_relationship_service
                    )
                    if resource.service_name != 'ec2':
                        resource.assume_role(self.role.arn)
        if len(items) > 0:
            logger.info('Add resources {}'.format(items))
            self.table.add(items)

    def exclude(self, resource_generator):
        items = []
        for resource in resource_generator:
            logger.debug('include resource {}'.format(resource.arn))
            if resource.arn:
                items.append({
                    'policy': self.policy.arn,
                    'arn': resource.arn
                })
            if resource.assumed_role != self.role.name:
                resource.detach_policy(self.policy.arn)
            else:
                resource.stop_assume_role(self.role.name)
        if len(items) > 0:
            logger.info('Remove resources {}'.format(items))
            self.table.remove(items)
