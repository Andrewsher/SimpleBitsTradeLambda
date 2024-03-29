from decimal import Decimal
import datetime
import json

from Model.AbstractRecord import AbstractRecord
from Model.AbstractRecord import AbstractRecordBuilder
from Model.TxnType import TxnType

class TransactionListRecordBuilder(AbstractRecordBuilder):
    def __init__(self):
        super().__init__()
        self.user = None
        self.txn_type = None
        self.currency = None
        self.bits = Decimal("0")
        self.usdt = Decimal("0")
        self.price = Decimal("0")
        self.bits_before_txn = None
        self.bits_after_txn = None
        self.usdt_before_txn = None
        self.usdt_after_txn = None
        self.extension_info = None

    def with_user(self, user:str):
        self.user = user
        return self

    def with_txn_type(self, txn_type: TxnType):
        self.txn_type = txn_type
        return self

    def with_currency(self, currency: str):
        self.currency = str(currency)
        return self

    def with_bits(self, bits):
        self.bits = Decimal(bits)
        return self

    def with_usdt(self, usdt):
        self.usdt = Decimal(usdt)
        return self

    def with_price(self, price):
        self.price = Decimal(price)
        return self

    def with_bits_before_txn(self, bits_before_txn):
        self.bits_before_txn = Decimal(bits_before_txn)
        return self

    def with_bits_after_txn(self, bits_after_txn):
        self.bits_after_txn = Decimal(bits_after_txn)
        return self

    def with_usdt_before_txn(self, usdt_before_txn):
        self.usdt_before_txn = Decimal(usdt_before_txn)
        return self

    def with_usdt_after_txn(self, usdt_after_txn):
        self.usdt_after_txn = Decimal(usdt_after_txn)
        return self

    def with_extension_info(self, extension_info):
        self.extension_info = str(extension_info)
        return self

    def build(self):
        transactionListRecord = TransactionListRecord()
        transactionListRecord.user = self.user
        transactionListRecord.create_time = self.create_time
        transactionListRecord.txn_type = self.txn_type
        transactionListRecord.currency = self.currency
        transactionListRecord.bits = self.bits
        transactionListRecord.usdt = self.usdt
        transactionListRecord.price = self.price
        transactionListRecord.bits_before_txn = self.bits_before_txn
        transactionListRecord.bits_after_txn = self.bits_after_txn
        transactionListRecord.usdt_after_txn = self.usdt_after_txn
        transactionListRecord.extension_info = self.extension_info
        return transactionListRecord


class TransactionListRecord(AbstractRecord):
    def __init__(self):
        super().__init__()
        # Primary Key
        self.user = None
        self.txn_type = None
        self.currency = None
        self.bits = Decimal("0")
        self.usdt = Decimal("0")
        self.price = Decimal("0")
        self.bits_before_txn = None
        self.bits_after_txn = None
        self.usdt_before_txn = None
        self.usdt_after_txn = None
        self.extension_info = None

    def to_dict(self):
        obj_dict = self.__dict__
        obj_dict["txn_type"] = self.txn_type.value
        obj_dict["create_time"] = self.create_time.isoformat()
        obj_dict["last_update_time"] = self.last_update_time.isoformat() if self.last_update_time else None
        return obj_dict

    @staticmethod
    def from_dict(obj_dict):
        # TODO: refind type
        builder = TransactionListRecordBuilder() \
            .with_user(obj_dict["user"]) \
            .with_create_time(obj_dict["create_time"]) \
            .with_txn_type(obj_dict["txn_type"]) \
            .with_currency(obj_dict["currency"]) \
            .with_bits(obj_dict["bits"]) \
            .with_usdt(obj_dict["usdt"]) \
            .with_price(obj_dict["price"])
        if "bits_before_txn" in obj_dict:
            builder.with_bits_before_txn(obj_dict["bits_before_txn"])
        if "bits_after_txn" in obj_dict:
            builder.with_bits_after_txn(obj_dict["bits_after_txn"])
        if "usdt_before_txn" in obj_dict:
            builder.with_usdt_before_txn(obj_dict["usdt_before_txn"])
        if "usdt_after_txn" in obj_dict:
            builder.with_usdt_after_txn(obj_dict["usdt_after_txn"])
        if "extension_info" in obj_dict:
            builder.with_extension_info(obj_dict["extension_info"])
        return builder.build()
