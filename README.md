# SimpleBitsTradeLambda
AWS Lambda function code for a simple bits trade system

## How to Use
1. Create SNS topic and subscription on console
2. Create DynamoDB
3. Create Lambda layer using the Binance Python zip file in Linux.

```shell
mkdir python
pip install --target ./python binance-connector urllib3==1.26.11
zip -r Binance-Python.zip python/*
aws s3 cp Binance-Python.zip {YOUR_S3_LOCATION}
# Create layer on console
...
```
4. Create Lambda Function
```shell
zip -r ../SimpleBitsTradeLambda.zip \
 Dao/* \
 Handler/* \
 Model/* \
 lambda_function.py \
 LICENSE \
 README.md 
# Create function on console
```

## Something We Need to Know before Deployment
1. Binance API is not available in US. Please deploy the resources (Lambda, SNS, S3, DynamoDB, etc.) to other regions like Singapore, Tokyo and Seoul.

