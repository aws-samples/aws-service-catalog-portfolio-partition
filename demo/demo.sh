#!/bin/bash

profile=$2
region=$3
keypair=sc-demo-key-pair
bucketname=service-catalog-portfolio-security-partition-$region

if [ $1 = 'build' ]
then
    aws --profile $profile --region $region s3 mb s3://$bucketname --region $region
    aws --profile $profile --region $region s3 cp ./demo/ s3://$bucketname/demo/ --recursive
    cd code/; zip -r code.zip ./*; cd ..
    aws --profile $profile --region $region s3 cp ./code/code.zip s3://$bucketname/solution/code.zip
    aws --profile $profile --region $region s3 cp ./deployment/template.yml s3://$bucketname/solution/template.yml
    aws --profile $profile --region $region ec2 create-key-pair --key-name $keypair
    aws --profile $profile --region $region cloudformation \
        create-stack \
            --stack-name security-partition-solution \
            --template-url https://s3.amazonaws.com/$bucketname/solution/template.yml \
            --parameters ParameterKey=LambdaCodeS3Bucket,ParameterValue=$bucketname ParameterKey=LambdaCodeS3Key,ParameterValue=solution/code.zip \
            --capabilities CAPABILITY_NAMED_IAM
    aws --profile $profile --region $region cloudformation \
        create-stack \
            --stack-name portfolios \
            --template-url https://s3.amazonaws.com/$bucketname/demo/portfolios.yml \
            --parameters ParameterKey=TemplatesS3Url,ParameterValue=https://s3.amazonaws.com/$bucketname/demo/products/ \
            --capabilities CAPABILITY_NAMED_IAM
fi

if [ $1 = 'destroy' ]
then
    aws --profile $profile --region $region cloudformation \
        delete-stack \
        --stack-name SC-Neptun-launch-products
    aws --profile $profile --region $region cloudformation \
        delete-stack \
        --stack-name SC-Uranus-launch-products

    pplist=`aws --profile $profile --region $region servicecatalog scan-provisioned-products --access-level-filter Key=Account,Value=self --query "ProvisionedProducts[].Id" --output text`
    for pp in $pplist
    do
        aws --profile $profile --region $region servicecatalog terminate-provisioned-product --provisioned-product-id $pp --ignore-errors
    done
    stacklist=`aws --profile $profile --region $region cloudformation list-stacks --stack-status-filter CREATE_FAILED CREATE_COMPLETE ROLLBACK_IN_PROGRESS --query "StackSummaries[].StackName | [?contains(@, 'SC-')]" --output text`
    for st in $stacklist
    do
        aws --profile $profile --region $region cloudformation delete-stack --stack-name $st
    done
    aws --profile $profile --region $region cloudformation \
        delete-stack \
        --stack-name portfolios
    aws --profile $profile --region $region cloudformation \
        delete-stack \
        --stack-name security-partition-solution
    aws --profile $profile --region $region s3 rb s3://$bucketname --force
    aws --profile $profile --region $region ec2 delete-key-pair --key-name $keypair

fi
