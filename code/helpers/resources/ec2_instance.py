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
import time
import re
from botocore.exceptions import ClientError

from helpers.resources.base import Base
from helpers.exceptions import MissingTrustRelationshipError


class EC2Instance(Base):

    def _arn(self):
        pattern = '[a-z]+-[a-z]+-\d'
        jmespath_az = "Reservations[].Instances[?InstanceId=='{}'].\
            Placement.AvailabilityZone | [0][0]".format(self.physical_id)
        jmespath_account = "Reservations[].OwnerId | [0]"
        data = self._client.describe_instances(InstanceIds=[self.physical_id])
        account = jmespath.search(jmespath_account, data)
        az = jmespath.search(jmespath_az, data)
        if az and account:
            region = re.match(pattern, az).group()
            return 'arn:aws:ec2:{region}:{account}:instance/{instance}'.format(
                region=region,
                account=account,
                instance=self.physical_id
            )
        return self.physical_id

    def _service_name(self):
        return 'ec2'

    def _access_to(self):
        return True

    def _access_from(self):
        return True

    def _assumed_role(self):
        profile_arn = self.get_instance_profile()
        if profile_arn:
            profile_name = profile_arn.split('/')[-1]
            instance_profile = self._iam_resource.InstanceProfile(profile_name)
            try:
                instance_profile.delete()
                return None
            except ClientError as e:
                if e.response['Error']['Code'] == 'DeleteConflict':
                    role = instance_profile.roles[0].name
                    return role
                else:
                    raise e
        return None

    def _statement_id(self):
        return 'DedicatedForResourceTypeEC2'

    def _trust_relationship_service(self):
        return "ec2.amazonaws.com"

    def _actions(self):
        return "*"

    def assume_role(self, role):
        if self.assumed_role:
            return
        prefix = role.split('/')[-1]
        profile_name = prefix + self.physical_id
        try:
            profile_arn = self._iam_client.create_instance_profile(
                InstanceProfileName=profile_name,
                Path='/'+prefix+'/'
            )['InstanceProfile']['Arn']
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                profile_arn = self._iam_resource.InstanceProfile(profile_name).arn
        try:
            self._iam_client.add_role_to_instance_profile(
                InstanceProfileName=profile_name,
                RoleName=prefix
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidParameterValue':
                time.sleep(15)
                self._iam_client.add_role_to_instance_profile(
                    InstanceProfileName=profile_name,
                    RoleName=prefix
                )
            elif e.response['Error']['Code'] == 'LimitExceeded':
                pass
            else:
                raise e
        try:
            self._client.associate_iam_instance_profile(
                IamInstanceProfile={'Arn': profile_arn},
                InstanceId=self.physical_id
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidParameterValue':
                time.sleep(15)
                self._client.associate_iam_instance_profile(
                    IamInstanceProfile={'Arn': profile_arn},
                    InstanceId=self.physical_id
                )
            elif e.response['Error']['Code'] == 'IncorrectState':
                pass
            else:
                raise e
        trust_service = jmespath.search(
            "Statement[].Principal.Service | contains(@, '{}')".format(self.service_name),
            self._iam_resource.Role(prefix).assume_role_policy_document
        )
        if not trust_service:
            raise MissingTrustRelationshipError()

    def stop_assume_role(self, role):
        try:
            profile_arn = self.get_instance_profile()
            instance_profile = self._iam_resource.InstanceProfile(profile_arn)
            instance_profile.remove_role(RoleName=role.split('/')[-1])
            for association in self.get_association_id():
                self._client.disassociate_iam_instance_profile(
                    AssociationId=association
                )
            instance_profile.delete()
        except:
            pass

    def get_instance_profile(self):
        data = self._client.describe_iam_instance_profile_associations(
            Filters=[{'Name': 'instance-id', 'Values': [self.physical_id]},
                     {'Name': 'state', 'Values': ['associated']}]
        )
        profile_arn = jmespath.search(
            "IamInstanceProfileAssociations[?InstanceId=='{}']\
            .IamInstanceProfile.Arn | [0]".format(self.physical_id),
            data
        )
        return profile_arn

    def get_association_id(self):
        data = self._client.describe_iam_instance_profile_associations(
            Filters=[{'Name': 'instance-id', 'Values': [self.physical_id]},
                     {'Name': 'state', 'Values': ['associated']}]
        )
        associations = jmespath.search(
            "IamInstanceProfileAssociations[?InstanceId=='{}']\
            .AssociationId".format(self.physical_id),
            data
        )
        return associations
