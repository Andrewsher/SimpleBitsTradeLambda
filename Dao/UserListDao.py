import boto3
from boto3.dynamodb.conditions import Key

class UserListDao:
    def __init__(self):
        self.dyn_resource = boto3.resource("dynamodb")
        self.table = self.dyn_resource.Table("user_list")

    def get_item(self, user, create_time):
        return self.table.get_item(Key={"user": user, "create_time": create_time})["Item"]

    def query(self, user):
        return self.table.query(KeyConditionExpression=Key('user').eq(user))

    def write(self, item):
        self.table.put_item(Item=item)
