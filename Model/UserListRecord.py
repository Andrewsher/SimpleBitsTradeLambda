from decimal import Decimal
import datetime
import json

from Model.AbstractRecord import AbstractRecord
from Model.AbstractRecord import AbstractRecordBuilder
from UserStatus import UserStatus

class UserListRecordBuilder(AbstractRecordBuilder):
    def __int__(self):
        super().__int__()
        # Primary Key
        self.user = None
        self.cur_bits = Decimal("0")
        self.cur_usdt = Decimal("0")
        self.init_bits = Decimal("0")
        self.init_usdt = Decimal("0")
        self.expected_buy_price = Decimal("0")
        self.expected_sell_price = Decimal("0")
        self.has_position = False
        self.status = UserStatus.NORMAL

    def with_user(self, user):
        self.user = user
        return self
    def with_cur_bits(self, cur_bits):
        self.cur_bits = Decimal(cur_bits)
        return self
    def with_cur_usdt(self, cur_usdt):
        self.cur_usdt = Decimal(cur_usdt)
        return self
    def with_init_bits(self, init_bits):
        self.init_bits = Decimal(init_bits)
        return self
    def with_init_usdt(self, init_usdt):
        self.init_usdt = Decimal(init_usdt)
        return self
    def with_status(self, status: UserStatus):
        self.status = UserStatus(status)
        return self
    def with_expected_buy_price(self, expected_buy_price):
        self.expected_buy_price = Decimal(expected_buy_price)
        return self
    def with_expected_sell_price(self, expected_sell_price):
        self.expected_sell_price = Decimal(expected_sell_price)
        return self
    def with_has_position(self, has_position):
        self.has_position = has_position
        return self
    def build(self):
        user_list_record = UserListRecord()
        user_list_record.set_user(self.user)
        user_list_record.set_create_time(self.create_time)
        user_list_record.set_last_update_time(self.last_update_time)
        user_list_record.set_cur_bits(self.cur_bits)
        user_list_record.set_cur_usdt(self.cur_usdt)
        user_list_record.set_init_bits(self.init_bits)
        user_list_record.set_init_usdt(self.init_usdt)
        user_list_record.set_status(self.status)
        user_list_record.set_expected_buy_price(self.expected_buy_price)
        user_list_record.set_expected_sell_price(self.expected_sell_price)
        user_list_record.set_has_position(self.has_position)
        return user_list_record

class UserListRecord(AbstractRecord):
    def __int__(self):
        super().__int__()
        self.user = None
        self.cur_bits = Decimal("0")
        self.cur_usdt = Decimal("0")
        self.init_bits = Decimal("0")
        self.init_usdt = Decimal("0")
        self.expected_buy_price = Decimal("0")
        self.expected_sell_price = Decimal("0")
        self.has_position = False
        self.status = UserStatus.NORMAL

    def set_user(self, user: str):
        self.user = user

    def set_cur_bits(self, cur_bits: Decimal):
        self.cur_bits = Decimal(cur_bits)

    def set_cur_usdt(self, cur_usdt: Decimal):
        self.cur_usdt = Decimal(cur_usdt)

    def set_init_bits(self, init_bits: Decimal):
        self.init_bits = Decimal(init_bits)

    def set_init_usdt(self, init_usdt: Decimal):
        self.init_usdt = Decimal(init_usdt)

    def set_status(self, status: UserStatus):
        self.status = UserStatus(status)

    def set_expected_buy_price(self, expected_buy_price: Decimal):
        self.expected_buy_price = Decimal(expected_buy_price)
        return self

    def set_expected_sell_price(self, expected_sell_price: Decimal):
        self.expected_sell_price = Decimal(expected_sell_price)

    def set_has_position(self, has_position: bool):
        self.has_position = has_position

    def is_active_user(self):
        return self.status == UserStatus.NORMAL

    @staticmethod
    def from_dict(obj_dict):
        return UserListRecordBuilder() \
            .with_user(obj_dict["user"]) \
            .with_create_time(obj_dict["create_time"]) \
            .with_last_update_time(obj_dict["last_update_time"]) \
            .with_cur_bits(obj_dict["cur_bits"] if "cur_bits" in obj_dict else Decimal("0")) \
            .with_cur_usdt(obj_dict["cur_usdt"] if "cur_usdt" in obj_dict else Decimal("0")) \
            .with_init_bits(obj_dict["init_bits"] if "init_bits" in obj_dict else Decimal("0")) \
            .with_init_usdt(obj_dict["init_usdt"] if "init_usdt" in obj_dict else Decimal("0")) \
            .with_expected_buy_price(obj_dict["expected_buy_price"] if "expected_buy_price" in obj_dict else Decimal("0")) \
            .with_expected_sell_price(obj_dict["expected_sell_price"] if "expected_sell_price" in obj_dict else Decimal("0")) \
            .build()
