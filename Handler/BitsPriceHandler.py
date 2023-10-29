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
from Model.TransactionListRecord import TransactionListRecord
from Model.TransactionListRecord import TransactionListRecordBuilder
from Model.TxnType import TxnType

class BitsPriceHandler():

    START_PROCESS_LOG = "[{}] Start to process message {}"
    WARN_PROCRESS_LOG = "[{}] WARN: {}"
    ERROR_PROCESS_LOG = "[{}] Failed to process message {} with error {}"
    CREATE_USER_MODE = "CREATE_USER"
    CLOSE_USER_MODE = "CLOSE_USER"
    CALCULATE_PROFIT_MODE = "CALCULATE_PROFIT"
    DEFAULT_MODE = "TRIGGER_TRANSACTION"
    NOTIFY_SNS_ARN = "arn:aws:sns:ap-southeast-1:672682740254:DeliverMessageToEmail" # TODO: get arn from SecretManager
    SNS_MESSAGE_CREATE_USER_SUBJECT = "Create Digital Coin Trade User"
    SNS_MESSAGE_CLOSE_USER_SUBJECT = "Close Digital Coin Trade User"
    SNS_MESSAGE_PROFIT_CALCULATION_SUBJECT = "Profit Calculation Result"
    SNS_MESSAGE_TXN_SUBJECT = "Digital Coin Transaction"
    LOWEST_POSITION = {
        "BTC": Decimal("0.2"),
        "ETH":  Decimal("2")
    }
    LOWEST_UDST = Decimal("100")
    AVAIL_CURRENCY = {
        "BTC",
        "ETH",
        "BNB",
        "XRP",
        "SOL",
        "ADA",
        "DOGE",
        "TRX",
        "LINK"
    }
    BINANCE_URL = "https://api.binance.com"

    def __init__(self):
        self.user_list_dao = UserListDao()
        self.txn_list_dao = TransactionListDao()
        self.event = None
        self.user_record: UserListRecord = None
        self.txn_record: TransactionListRecord = None
        self.mode = None
        self.price = None
        self.currency = None
        self.sns_client = None
        config_logging(logging, logging.INFO)
        self.spot_client = Client(base_url=BitsPriceHandler.BINANCE_URL)

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
                self.__calculate_profit(subject=BitsPriceHandler.SNS_MESSAGE_PROFIT_CALCULATION_SUBJECT)
            else:
                self.__trigger_transaction()
        except Exception as e:
            print(BitsPriceHandler.ERROR_PROCESS_LOG.format(
                datetime.utcnow().isoformat(),
                event,
                e
            ))
            raise e

    def __create_user(self):
        if self.user_record and self.user_record.is_active_user():
            print(BitsPriceHandler.WARN_PROCRESS_LOG.format(
                datetime.utcnow().isoformat(),
                f"Active user {self.event['user']} already exists, please user another user name"
            ))
            return
        self.user_record: UserListRecord = UserListRecordBuilder() \
            .with_user(self.event["user"]) \
            .with_currency(self.event["currency"]) \
            .with_create_time(datetime.utcnow()) \
            .with_last_update_time(datetime.utcnow()) \
            .with_cur_usdt(decimal.Decimal(self.event["init_usdt"])) \
            .with_init_usdt(decimal.Decimal(self.event["init_usdt"])) \
            .with_expected_buy_price(self.price * Decimal("0.5")) \
            .build()

        self.txn_record: TransactionListRecord = TransactionListRecordBuilder() \
            .with_user(self.event["user"]) \
            .with_create_time(datetime.utcnow()) \
            .with_last_update_time(datetime.utcnow()) \
            .with_txn_type(TxnType.CREATE_USER) \
            .with_currency(self.event["currency"]) \
            .with_bits_after_txn(Decimal("0")) \
            .with_usdt_after_txn(Decimal(self.event["init_usdt"])) \
            .build()

        self.__write_user_to_db()
        self.__write_txn_to_db()
        self.__notify(
            subject=BitsPriceHandler.SNS_MESSAGE_CREATE_USER_SUBJECT,
            message=f"""
                Create user succeed!
                User name: {self.user_record.user}
                Currency: {self.user_record.currency}
                Init USDT: {self.user_record.init_usdt}
                Create time: {self.user_record.create_time}
            """)
        return

    def __close_user(self):
        if not self.user_record:
            return
        if self.user_record.cur_bits > Decimal("0"):
            self.__sell_all()
        else:
            self.txn_record = TransactionListRecordBuilder() \
                .with_user(self.user_record.user) \
                .with_create_time(datetime.utcnow()) \
                .with_txn_type(TxnType.CLOSE_USER) \
                .with_currency(self.user_record.currency) \
                .with_bits(Decimal("0")) \
                .with_usdt(Decimal("0")) \
                .with_price(self.price) \
                .with_bits_before_txn(self.user_record.cur_bits) \
                .with_bits_after_txn(self.user_record.cur_bits) \
                .with_usdt_before_txn(self.user_record.cur_usdt) \
                .with_usdt_after_txn(self.user_record.cur_usdt) \
                .build()
        self.user_record.set_status(UserStatus.CLOSED)
        self.__write_user_to_db()
        self.__write_txn_to_db()
        self.__calculate_profit(
            subject=BitsPriceHandler.SNS_MESSAGE_CLOSE_USER_SUBJECT,
            base_str=f"Close User {self.user_record.user} succeed"
        )
        return

    def __trigger_transaction(self):
        if self.price <= self.user_record.expected_buy_price:
            if self.user_record.cur_usdt <= BitsPriceHandler.LOWEST_UDST:
                pass
            elif self.user_record.cur_bits == Decimal("0"):
                self.__buy(self.user_record.cur_usdt / self.price / 2)
                self.user_record.set_expected_sell_price(
                    self.user_record.current_position_cost / self.user_record.cur_bits * 2)
                self.__write_user_to_db()
                self.__write_txn_to_db()
                self.__calculate_profit_in_txn()
            elif self.price < self.user_record.expected_buy_price * Decimal("0.5"):
                self.__buy(self.user_record.cur_usdt / self.price)
                self.user_record.set_expected_sell_price(
                    self.user_record.current_position_cost / self.user_record.cur_bits * 2)
                self.__write_user_to_db()
                self.__write_txn_to_db()
                self.__calculate_profit_in_txn()

        elif self.price > self.user_record.expected_buy_price * 2:
            self.user_record.expected_buy_price = self.price * Decimal("0.5")
            self.__write_user_to_db()

        if self.user_record.cur_bits > Decimal("0") and self.price > self.user_record.expected_sell_price:
            if self.user_record.cur_bits <= BitsPriceHandler.LOWEST_POSITION[self.user_record.currency]:
                self.__sell(self.user_record.cur_bits)
                self.__write_user_to_db()
                self.__write_txn_to_db()
                self.__calculate_profit_in_txn()
            else:
                self.__sell(self.user_record.cur_bits / 2)
                self.user_record.set_expected_sell_price(self.user_record.expected_sell_price * 2)
                self.__write_user_to_db()
                self.__write_txn_to_db()
                self.__calculate_profit_in_txn()

        return

    def __calculate_profit_in_txn(self):
        assert self.txn_record.txn_type in {TxnType.BUY, TxnType.SELL, TxnType.BUY.name, TxnType.SELL.name}
        self.__calculate_profit(
            subject=BitsPriceHandler.SNS_MESSAGE_TXN_SUBJECT,
            base_str=f"User: {self.user_record.user}"
                     + f"\n{self.txn_record.txn_type} {self.txn_record.bits} {self.user_record.currency} "
                     + f"at {self.price} USDT"
                     + f"\nCost {self.txn_record.usdt} USDT"
                     + f"\n USDT before txn: {self.txn_record.usdt_before_txn}"
                     + f"\n {self.user_record.currency} before txn: {self.txn_record.bits_before_txn}"
        )

    def __calculate_profit(self, subject, base_str=None):
        s = ""
        if base_str:
            s += base_str
        s += f"\nUser: {self.user_record.user}"
        s += f"\nInit USDT: {self.user_record.init_usdt}"
        s += f"\nInit Bits Unit: {self.user_record.init_bits}"
        init_assets = self.user_record.init_usdt + self.user_record.init_bits * self.price
        s += f"\nInit assets: {init_assets}"
        s += f"\nCurrent USDT: {self.user_record.cur_usdt}"
        s += f"\nCurrent Bits Unit: {self.user_record.cur_bits}"
        s += f", which deserves {self.user_record.cur_bits * self.price}"
        cur_asset = self.user_record.cur_usdt + self.user_record.cur_bits * self.price
        s += f"\nCurrent assets: {cur_asset} USDT"
        s += f"\nProfit rate: {round((cur_asset / init_assets - 1) * 100, 2)} %"
        if isinstance(self.user_record.create_time, datetime):
            passed_time = datetime.utcnow() - self.user_record.create_time
        elif isinstance(self.user_record.create_time, str):
            passed_time = datetime.utcnow() - datetime.fromisoformat(self.user_record.create_time)
        s += f"\nPassed {passed_time.days} days, {passed_time.seconds} seconds"
        years = Decimal(passed_time.total_seconds()) / (86400 * 365)
        s += f"\nPassed {round(years, 2)} years"
        if years > Decimal("0.2"):
            s += f"\nYearly profit rate: {round((math.pow(cur_asset / init_assets, 1 / years) - 1) * 100, 2)} %"
        print(s)
        self.__notify(subject, s)
        return

    def __query_user(self, user_name):
        queried_user = self.user_list_dao.get_latest_item(user_name)
        if self.mode == BitsPriceHandler.CREATE_USER_MODE:
            return UserListRecord.from_dict(queried_user) if queried_user else None
        if not queried_user or not UserListRecord.from_dict(queried_user).is_active_user():
            raise BitsPriceHandler.WARN_PROCRESS_LOG.format(
                datetime.utcnow().isoformat(),
                f"Cannot get active user {user_name} because it does not exist or already been closed"
            )
        user_list_record: UserListRecord = UserListRecord.from_dict(queried_user)
        return user_list_record

    def __get_price(self):
        self.__get_currency()
        price_dict = self.spot_client.ticker_price(self.currency + "USDT")
        print(price_dict)
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
        self.txn_record = TransactionListRecordBuilder() \
            .with_user(self.user_record.user) \
            .with_create_time(datetime.utcnow()) \
            .with_last_update_time(datetime.utcnow()) \
            .with_txn_type(TxnType.BUY) \
            .with_currency(self.user_record.currency) \
            .with_bits(bits_unit) \
            .with_usdt(self.price * bits_unit) \
            .with_price(self.price) \
            .with_bits_before_txn(self.user_record.cur_bits) \
            .with_bits_after_txn(self.user_record.cur_bits + bits_unit) \
            .with_usdt_before_txn(self.user_record.cur_usdt) \
            .with_usdt_after_txn(self.user_record.cur_usdt - self.price * bits_unit) \
            .build()
        self.user_record.set_current_position_cost(self.user_record.current_position_cost + bits_unit * self.price)
        self.user_record.set_cur_bits(self.user_record.cur_bits + bits_unit)
        self.user_record.set_cur_usdt(self.user_record.cur_usdt - bits_unit * self.price)
        self.user_record.set_last_update_time(datetime.utcnow())
        return

    def __sell_all(self):
        self.__sell(self.user_record.cur_bits)
        return

    def __sell(self, bits_unit: Decimal):
        assert self.user_record.cur_bits >= bits_unit
        # TODO: 线上购买
        self.txn_record = TransactionListRecordBuilder() \
            .with_user(self.user_record.user) \
            .with_create_time(datetime.utcnow()) \
            .with_txn_type(TxnType.SELL) \
            .with_currency(self.user_record.currency) \
            .with_bits(bits_unit) \
            .with_usdt(self.price * bits_unit) \
            .with_price(self.price) \
            .with_bits_before_txn(self.user_record.cur_bits) \
            .with_bits_after_txn(self.user_record.cur_bits - bits_unit) \
            .with_usdt_before_txn(self.user_record.cur_usdt) \
            .with_usdt_after_txn(self.user_record.cur_usdt + self.price * bits_unit) \
            .build()
        self.user_record.set_current_position_cost(self.user_record.current_position_cost * (1 - bits_unit / self.user_record.cur_bits))
        self.user_record.set_cur_bits(self.user_record.cur_bits - bits_unit)
        self.user_record.set_cur_usdt(self.user_record.cur_usdt + self.price * bits_unit)
        self.user_record.set_last_update_time(datetime.utcnow())
        return

    def __notify(self, subject, message):
        if not self.sns_client:
            self.sns_client = boto3.client("sns")
        self.sns_client.publish(
            TargetArn=BitsPriceHandler.NOTIFY_SNS_ARN,
            Message=message,
            Subject=subject
        )
        return

    def __write_user_to_db(self):
        self.user_list_dao.write(self.user_record.to_dict())
        return

    def __write_txn_to_db(self):
        self.txn_list_dao.write(self.txn_record.to_dict())
        return
