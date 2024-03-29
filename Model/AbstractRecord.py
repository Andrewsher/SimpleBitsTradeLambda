from decimal import Decimal
import datetime


class AbstractRecordBuilder():
    def __init__(self):
        self.create_time = None
        self.last_update_time = None

    def with_create_time(self, create_time):
        self.create_time = create_time
        return self
    def with_last_update_time(self, last_update_time):
        self.last_update_time = last_update_time
        return self

    def build(self):
        user_list_record = AbstractRecord()
        user_list_record.set_create_time(self.create_time)
        user_list_record.set_last_update_time(self.last_update_time)
        return user_list_record

class AbstractRecord():
    def __init__(self):
        # Sort Key
        self.create_time = None
        self.last_update_time = None

    def set_create_time(self, create_time: datetime.datetime):
        self.create_time = create_time

    def set_last_update_time(self, last_update_time: datetime.datetime):
        self.last_update_time = last_update_time

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(obj_dict):
        return AbstractRecordBuilder() \
            .with_create_time(obj_dict["create_time"]) \
            .with_last_update_time(obj_dict["last_update_time"]) \
            .build()
