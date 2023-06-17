import boto3
from boto3.dynamodb.conditions import Key

class TransactionListDao:
    def __init__(self):
        self.dyn_resource = boto3.resource("dynamodb")
        self.table = self.dyn_resource.Table("transaction_list")

    def get_item(self, user, datetime):
        return self.table.get_item(Key={"user": user, "datetime": datetime})["Item"]

    def query(self, user):
        return self.table.query(KeyConditionExpression=Key('user').eq(user))

    def write(self, item):
        self.table.put_item(Item=item)
