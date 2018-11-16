1. Run demo.sh:
```
cd aws-service-catalog-portfolio-security-partition/
./demo/demo.sh build
```
1. console login as scuserUranus
create stack with
template: `https://s3.amazonaws.com/service-catalog-portfolio-security-partition-us-east-1/demo/launch_productsA.yml`
name: SC-Uarnus-launch-products
1. console login as scuserNeptun
create stack with
template: `https://s3.amazonaws.com/service-catalog-portfolio-security-partition-us-east-1/demo/launch_productsB.yml`
name: SC-Neptun-launch-products
1. Cleanup: to delete all resources:
```
cd aws-service-catalog-portfolio-security-partition/
./demo/demo.sh destroy
```
