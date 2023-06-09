from decimal import Decimal
import datetime

from UserStatus import UserStatus

class UserListRecordBuilder():
    def __int__(self):
        self.user = None
        self.create_time = None
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
    def with_create_time(self, create_time):
        self.create_time = Decimal(create_time)
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
        user_list_record.set_cur_bits(self.cur_bits)
        user_list_record.set_cur_usdt(self.cur_usdt)
        user_list_record.set_init_bits(self.init_bits)
        user_list_record.set_init_usdt(self.init_usdt)
        user_list_record.set_status(self.status)
        user_list_record.set_expected_buy_price(self.expected_buy_price)
        user_list_record.set_expected_sell_price(self.expected_sell_price)
        user_list_record.set_has_position(self.has_position)
        return user_list_record

class UserListRecord():
    def __int__(self):
        self.user = None
        self.create_time = None
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

    def set_create_time(self, create_time: datetime.datetime):
        self.create_time = create_time

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
