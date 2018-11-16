# Supporting new Resource Types
When it comes to IAM, each AWS resource type might have a different behavior. Moreover, there are resource types which are actively accessing other resources and thus might assume roles (e.g., ec2 instance, lambda function) while others are more passive (e.g., s3, dynamoDB). To handle the different resources, the portfolio security partition implementation maintain a whitelist of supported resource types. In addition, to be supported, each resource type must implement the resources/base.py interface.
The following document is a step by step guide for adding support for unsupported resource type.

## Add support to "AWS::ServiceX::ResY"
To demonstrate the process, we will add a fake aws resource: "AWS::ServiceX::ResY"

#### Add the new resource type to the whitelist:
Aws-service-catalog-portfolio-partition/code/configuration/resource_types_supported.json
```json
{
 "Applicable": [
   "...",
   "...",
   "AWS::ServiceX::ResY"
 ],
 "NotApplicable": [
   "...",
   "..."
 ]
}
```
##### Applicable:   
- For supported resources which must be handled. 
- Must be the exact resource type name.

##### NotApplicable:
- For resources which should be ignored or not supported.
- Supports regex

If a resource type appears in the “Applicable” list it will be processed regardless its status in the “NotApplicable” list.

#### The Interface:
`code/helpers/resources/base.py`

Create new file:
```bash
aws-service-catalog-portfolio-partition/code/helpers/resources/servicex_resy.py
```
```python
from helpers.resources.base import Base

class ServicexResy(Base):

    # returns the ARN of the resource AWS::ServiceX::ResY
    def _arn(self):
        pass

    # returns the name of the service with which a “boto3.client” and “boto3.resource” will be instantiated
    def _service_name(self):
        return ‘servicex’

    # returns True when the resource should be accessed by other resources
    def _access_to(self):
        return True

    # returns True when the resource should assume role to access other resources
    def _access_from(self):
        return True

    # returns the arn of a role that the resource currently assumes or None when N/A
    def _assumed_role(self):
        pass

    # returns the name to be used for the statement id in the policy, to be dedicated for the resources of this type
    def _statement_id(self):
        return 'DedicatedForResourceTypeServiceXResY'

    # returns the service name as it should appear in a trust relationship policy document
    def _trust_relationship_service(self):
        return "servicex.amazonaws.com"

    # returns the actions to be allowed on this resource type (will be overridden by resource_types_actions_allowed.json)
    def _actions(self):
        return "*"

    # assumes the passed role and raise trust relationship missing error if the service isn’t listed in the role trust policy
    def assume_role(self, role):
        pass

    # detach the assumed role from the resource
    def stop_assume_role(self, role):
        pass
```

#### Lambda Functions Permissions
The permissions of the lambda functions' execution role must be updated with new allowed actions used in the new resource type object implementation. 
This should be done by updating the Aws-service-catalog-portfolio-partition/deployment/template.yml and update the relevant CFN stack.
