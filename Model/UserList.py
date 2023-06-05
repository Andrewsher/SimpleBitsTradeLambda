from decimal import Decimal
import enum

from UserStatus import UserStatus

class UserListBuilder():
    def __int__(self):
        self.user = None
        self.create_time = None
        self.cur_bits = Decimal("0")
        self.cur_usdt = Decimal("0")
        self.init_bits = Decimal("0")
        self.init_usdt = Decimal("0")
        self.status = UserStatus.NORMAL

    def user(self, user):
        self.user = user
        return self
    def create_time(self, create_time):
        self.create_time = Decimal(create_time)
        return self
    def cur_bits(self, cur_bits):
        self.cur_bits = Decimal(cur_bits)
        return self
    def cur_usdt(self, cur_usdt):
        self.cur_usdt = Decimal(cur_usdt)
        return self
    def init_bits(self, init_bits):
        self.init_bits = Decimal(init_bits)
        return self
    def init_usdt(self, init_usdt):
        self.init_usdt = Decimal(init_usdt)
        return self
    def status(self, status: UserStatus):
        self.status = UserStatus(status)
        return self
    def build(self):
        userList = UserList()
        userList.set_user(self.user)
        userList.set_create_time(self.create_time)
        userList.set_cur_bits(self.cur_bits)
        userList.set_cur_usdt(self.cur_usdt)
        userList.set_init_bits(self.init_bits)
        userList.set_init_usdt(self.init_usdt)
        userList.set_status(self.status)
        return userList

class UserList():
    def __int__(self):
        self.user = None
        self.create_time = None
        self.cur_bits = Decimal("0")
        self.cur_usdt = Decimal("0")
        self.init_bits = Decimal("0")
        self.init_usdt = Decimal("0")
        self.status = UserStatus.NORMAL

    def set_user(self, user):
        self.user = user
        return self

    def set_create_time(self, create_time):
        self.create_time = Decimal(create_time)
        return self

    def set_cur_bits(self, cur_bits):
        self.cur_bits = Decimal(cur_bits)
        return self

    def set_cur_usdt(self, cur_usdt):
        self.cur_usdt = Decimal(cur_usdt)
        return self

    def set_init_bits(self, init_bits):
        self.init_bits = Decimal(init_bits)
        return self

    def set_init_usdt(self, init_usdt):
        self.init_usdt = Decimal(init_usdt)
        return self

    def set_status(self, status: UserStatus):
        self.status = UserStatus(status)
        return self
