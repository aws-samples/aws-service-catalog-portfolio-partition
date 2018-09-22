PORTFOLIO_ID_TAG = 'aws:servicecatalog:portfolioArn'

APPLICABLE_FILE = 'configuration/resource_types_supported.json'
ACTIONS_FILE = 'configuration/resource_types_actions_allowed.json'
ALLOWED_ACTIONS = "*"

BASE_EMPTY_POLICY = '''{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Deny",
            "Action": "*",
            "Resource": "arn:aws:iam:::policy/notexist-2h46v9nd84hd7ndir4yd"
        }
    ]
}
'''
BASE_POLICY = BASE_EMPTY_POLICY

BASE_TRUST_POLICY = '''{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
'''
