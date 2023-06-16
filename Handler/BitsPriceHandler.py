import decimal
import random
from datetime import datetime
from decimal import Decimal
# import ccxt
import boto3
import math

from Dao.UserListDao import UserListDao
from Dao.TransactionListDao import TransactionListDao

from Model.UserListRecord import UserListRecord
from Model.UserListRecord import UserListRecordBuilder
from Model.UserStatus import UserStatus

class BitsPriceHandler():

    START_PROCESS_LOG = "[{}] Start to process message {}"
    WARN_PROCRESS_LOG = "[{}] WARN: {}"
    ERROR_PROCESS_LOG = "[{}] Failed to process message {} with error {}"
    CREATE_USER_MODE = "CREATE_USER"
    CLOSE_USER_MODE = "CLOSE_USER"
    CALCULATE_PROFIT_MODE = "CALCULATE_PROFIT"
    DEFAULT_MODE = "DEFAULT"
    SNS_MESSAGE_SUBJECT = "Profit Calculation Result"

    def __int__(self):
        self.user_list_dao = UserListDao()
        self.txn_list_dao = TransactionListDao()
        self.user_record = None
        self.mode = None
        self.price = None
        self.sns_client = None

    def handle_request(self, event: dict):
        print(BitsPriceHandler.START_PROCESS_LOG.format(
            datetime.utcnow().isoformat(),
            event
        ))
        try:
            self.mode = event["mode"]
            if self.mode == BitsPriceHandler.CREATE_USER_MODE:
                self.__create_user(event)
            elif self.mode == BitsPriceHandler.CLOSE_USER_MODE:
                self.__close_user(event)
            elif self.mode == BitsPriceHandler.CALCULATE_PROFIT_MODE:
                self.__calculate_profit_by_event(event)
            else:
                self.__trigger_transaction(event)
        except Exception as e:
            print(BitsPriceHandler.ERROR_PROCESS_LOG.format(
                datetime.utcnow().isoformat(),
                event,
                e
            ))

    def __create_user(self, event):
        queried_user = self.user_list_dao.get_latest_item(event["user"])
        if queried_user and UserListRecord.from_dict(queried_user).is_active_status():
            print(BitsPriceHandler.WARN_PROCRESS_LOG.format(
                datetime.utcnow().isoformat(),
                f"Active user {event['user']} already exists, please user another user name"
            ))
            return
        user_list_record = UserListRecordBuilder() \
            .with_user(event["user"]) \
            .with_create_time(datetime.utcnow().isoformat()) \
            .with_last_update_time(datetime.utcnow().isoformat()) \
            .with_cur_usdt(decimal.Decimal(event["init_usdt"])) \
            .with_init_usdt(decimal.Decimal(event["init_usdt"])) \
            .build()

        self.user_list_dao.write(user_list_record.to_dict())
        return

    def __close_user(self, event):
        user_list_record = self.__query_user(event["user"])
        price = self.__get_price()
        self.__sell_all(user_list_record, price)
        self.__calculate_profit(user_list_record)
        user_list_record.set_status(UserStatus.CLOSED)
        self.user_list_dao.write(user_list_record.to_dict())
        return

    def __calculate_profit_by_event(self, event):
        user_list_record = self.__query_user(event["user"])
        self.__calculate_profit(user_list_record)
        return

    def __query_user(self, user_name):
        queried_user = self.user_list_dao.get_latest_item(user_name)
        if not queried_user or not UserListRecord.from_dict(queried_user).is_active_status():
            print(BitsPriceHandler.WARN_PROCRESS_LOG.format(
                datetime.utcnow().isoformat(),
                f"Cannot close active user {user_name} because it does not exist"
            ))
            return
        user_list_record: UserListRecord = UserListRecord.from_dict(queried_user)
        return user_list_record

    def __sell_all(self, user_list_record: UserListRecord, price: Decimal):
        self.__sell(user_list_record, price, user_list_record.cur_bits)
        return

    def __buy_signal(self, price):
        return True

    def __buy(self, price):
        # do something
        pass

    def __get_price(self):
        # TODO: 获取实时价格
        self.price = Decimal(random.random())
        return self.price

    def __sell(self, user_list_record: UserListRecord, price: Decimal, bits_unit: Decimal):
        assert user_list_record.cur_bits >= bits_unit
        # TODO: 线上购买
        user_list_record.set_cur_bits(user_list_record.cur_bits - bits_unit)
        user_list_record.set_cur_usdt(user_list_record.cur_usdt + price * bits_unit)
        return

    def __calculate_profit(self, user_list_record: UserListRecord):
        s = f"Init USDT: {user_list_record.init_usdt}"
        s += f"\nInit Bits Unit: {user_list_record.init_bits}"
        init_assets = user_list_record.init_usdt +user_list_record.init_bits * self.price
        s += f"\nInit assets: {init_assets}"
        s += f"\nCurrent USDT: {user_list_record.cur_usdt}"
        s += f"\nCurrent Bits Unit: {user_list_record.cur_bits}"
        if not self.price:
            self.__get_price()
        s += f", which deserves {user_list_record.cur_bits * self.price}"
        cur_asset = user_list_record.cur_usdt + user_list_record.cur_bits * self.price
        s += f"\nCurrent assets: {cur_asset}"
        s += f"\nProfit rate: {round((cur_asset / init_assets - 1) * 100, 2)} %"
        passed_time = datetime.utcnow() - user_list_record.create_time
        s += f"\nPassed {passed_time.days} days, {passed_time.seconds} seconds"
        years = Decimal(passed_time.total_seconds()) / (86400 * 365)
        s += f"\nPassed {round(years, 2)} years"
        s += f"\nYearly profit rate: {round((math.pow(cur_asset / init_assets, 1 / years) - 1) * 100, 2)} %"
        print(s)
        self.__notify(s)
        return

    def __notify(self, message):
        if not self.sns_client:
            self.sns_client = boto3.client("sns")
        self.sns_client.publish(
            TargetArn="arn:aws:sns:us-west-2:672682740254:DeliverMessageToEmail",
            Message=message,
            Subject=BitsPriceHandler.SNS_MESSAGE_SUBJECT
        )
        return
