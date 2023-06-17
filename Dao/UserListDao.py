import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime

class UserListDao:
    def __init__(self):
        self.dyn_resource = boto3.resource("dynamodb")
        self.table = self.dyn_resource.Table("user_list")

    def get_item(self, user, create_time):
        return self.table.get_item(Key={"user": user, "create_time": create_time})["Item"]

    def get_latest_item(self, user):
        items: list = self.query(user)["Items"]
        if items:
            items.sort(key=lambda item: datetime.fromisoformat(item["create_time"]), reverse=True)
            return items[0]
        return None

    def query(self, user: str):
        return self.table.query(KeyConditionExpression=Key('user').eq(user))

    def write(self, item: dict):
        self.table.put_item(Item=item)
