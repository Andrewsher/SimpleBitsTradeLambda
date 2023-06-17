import decimal
import random
from datetime import datetime
from decimal import Decimal
import binance
import logging
from binance.spot import Spot as Client
from binance.lib.utils import config_logging
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
    DEFAULT_MODE = "TRIGGER_TRANSACTION"
    NOTIFY_SNS_ARN = "arn:aws:sns:us-west-2:672682740254:DeliverMessageToEmail"
    SNS_MESSAGE_SUBJECT = "Profit Calculation Result"
    LOWEST_POSITION = {
        "BTC": Decimal("0.2"),
        "ETH":  Decimal("2")
    }
    LOWEST_UDST = Decimal("100")
    AVAIL_CURRENCY = {
        "BTC",
        "ETH"
    }

    def __int__(self):
        self.user_list_dao = UserListDao()
        self.txn_list_dao = TransactionListDao()
        self.event = None
        self.user_record: UserListRecord = None
        self.mode = None
        self.price = None
        self.currency = None
        self.sns_client = None
        config_logging(logging, logging.INFO)
        self.spot_client = Client(base_url="https://testnet.binance.vision")

    def handle_request(self, event: dict):
        print(BitsPriceHandler.START_PROCESS_LOG.format(
            datetime.utcnow().isoformat(),
            event
        ))
        self.event = event
        try:
            self.mode = self.event["mode"]
            self.user_record = self.__query_user(self.event["user"])
            self.__get_price()
            if self.mode == BitsPriceHandler.CREATE_USER_MODE:
                self.__create_user()
            elif self.mode == BitsPriceHandler.CLOSE_USER_MODE:
                self.__close_user()
            elif self.mode == BitsPriceHandler.CALCULATE_PROFIT_MODE:
                self.__calculate_profit()
            else:
                self.__trigger_transaction()
        except Exception as e:
            print(BitsPriceHandler.ERROR_PROCESS_LOG.format(
                datetime.utcnow().isoformat(),
                event,
                e
            ))

    def __create_user(self):
        if self.user_record:
            print(BitsPriceHandler.WARN_PROCRESS_LOG.format(
                datetime.utcnow().isoformat(),
                f"Active user {self.event['user']} already exists, please user another user name"
            ))
            return
        self.user_record: UserListRecord = UserListRecordBuilder() \
            .with_user(self.event["user"]) \
            .with_currency(self.event["currency"]) \
            .with_create_time(datetime.utcnow().isoformat()) \
            .with_last_update_time(datetime.utcnow().isoformat()) \
            .with_cur_usdt(decimal.Decimal(self.event["init_usdt"])) \
            .with_init_usdt(decimal.Decimal(self.event["init_usdt"])) \
            .with_expected_buy_price(self.price * Decimal("0.5")) \
            .build()

        self.__write_user_to_db()
        return

    def __close_user(self):
        if not self.user_record:
            return
        self.__sell_all()
        self.__calculate_profit()
        self.user_record.set_status(UserStatus.CLOSED)
        self.__write_user_to_db()
        return

    def __trigger_transaction(self):
        if self.price <= self.user_record.expected_buy_price:
            if self.user_record.cur_usdt <= BitsPriceHandler.LOWEST_UDST:
                pass
            elif self.user_record.cur_bits == Decimal("0"):
                self.__buy(self.user_record.cur_usdt / self.price / 2)
                self.user_record.set_expected_sell_price(
                    self.user_record.current_position_cost / self.user_record.cur_bits * 2)
                self.__calculate_profit()
            elif self.price < self.user_record.expected_buy_price * Decimal("0.5"):
                self.__buy(self.user_record.cur_usdt / self.price)
                self.user_record.set_expected_sell_price(
                    self.user_record.current_position_cost / self.user_record.cur_bits * 2)
                self.__calculate_profit()

        elif self.price > self.user_record.expected_buy_price * 2:
            self.user_record.expected_buy_price = self.price * Decimal("0.5")

        if self.user_record.cur_bits > Decimal("0") and self.price > self.user_record.expected_sell_price:
            if self.user_record.cur_bits <= BitsPriceHandler.LOWEST_POSITION[self.user_record.currency]:
                self.__sell(self.user_record.cur_bits)
                self.__calculate_profit()
            else:
                self.__sell(self.user_record.cur_bits / 2)
                self.__calculate_profit()

        self.__write_user_to_db()
        return

    def __calculate_profit(self):
        s = f"Init USDT: {self.user_record.init_usdt}"
        s += f"\nInit Bits Unit: {self.user_record.init_bits}"
        init_assets = self.user_record.init_usdt +self.user_record.init_bits * self.price
        s += f"\nInit assets: {init_assets}"
        s += f"\nCurrent USDT: {self.user_record.cur_usdt}"
        s += f"\nCurrent Bits Unit: {self.user_record.cur_bits}"
        s += f", which deserves {self.user_record.cur_bits * self.price}"
        cur_asset = self.user_record.cur_usdt + self.user_record.cur_bits * self.price
        s += f"\nCurrent assets: {cur_asset}"
        s += f"\nProfit rate: {round((cur_asset / init_assets - 1) * 100, 2)} %"
        passed_time = datetime.utcnow() - self.user_record.create_time
        s += f"\nPassed {passed_time.days} days, {passed_time.seconds} seconds"
        years = Decimal(passed_time.total_seconds()) / (86400 * 365)
        s += f"\nPassed {round(years, 2)} years"
        s += f"\nYearly profit rate: {round((math.pow(cur_asset / init_assets, 1 / years) - 1) * 100, 2)} %"
        print(s)
        self.__notify(s)
        return

    def __query_user(self, user_name):
        queried_user = self.user_list_dao.get_latest_item(user_name)
        if not queried_user or not UserListRecord.from_dict(queried_user).is_active_status():
            print(BitsPriceHandler.WARN_PROCRESS_LOG.format(
                datetime.utcnow().isoformat(),
                f"Cannot get active user {user_name} because it does not exist or already been closed"
            ))
            return
        user_list_record: UserListRecord = UserListRecord.from_dict(queried_user)
        return user_list_record

    def __get_price(self):
        self.__get_currency()
        price_dict = self.spot_client.ticker_price(self.currency + "USDT")
        self.price = Decimal(price_dict["price"])
        return

    def __get_currency(self):
        if self.mode == BitsPriceHandler.CREATE_USER_MODE:
            self.currency = self.event["currency"]
        else:
            self.currency = self.user_record.currency
        assert self.currency in BitsPriceHandler.AVAIL_CURRENCY
        return

    def __buy(self, bits_unit: Decimal):
        assert self.user_record.cur_usdt >= bits_unit * self.price
        # TODO 线上购买
        self.user_record.set_current_position_cost(self.user_record.current_position_cost + bits_unit * self.price)
        self.user_record.set_cur_bits(self.user_record.cur_bits + bits_unit)
        self.user_record.set_cur_usdt(self.user_record.cur_usdt - bits_unit * self.price)
        return

    def __sell_all(self):
        self.__sell(self.user_record.cur_bits)
        return

    def __sell(self, bits_unit: Decimal):
        assert self.user_record.cur_bits >= bits_unit
        # TODO: 线上购买
        self.user_record.set_current_position_cost(self.user_record.current_position_cost * (1 - bits_unit / self.user_record.cur_bits))
        self.user_record.set_cur_bits(self.user_record.cur_bits - bits_unit)
        self.user_record.set_cur_usdt(self.user_record.cur_usdt + self.price * bits_unit)
        return

    def __notify(self, message):
        if not self.sns_client:
            self.sns_client = boto3.client("sns")
        self.sns_client.publish(
            TargetArn=BitsPriceHandler.NOTIFY_SNS_ARN,
            Message=message,
            Subject=BitsPriceHandler.SNS_MESSAGE_SUBJECT
        )
        return

    def __write_user_to_db(self):
        self.user_list_dao.write(self.user_record.to_dict())
        return
