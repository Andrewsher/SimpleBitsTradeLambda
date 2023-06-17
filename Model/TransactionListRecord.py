from decimal import Decimal
import datetime
import json

from Model.AbstractRecord import AbstractRecord
from Model.AbstractRecord import AbstractRecordBuilder
from TxnType import TxnType

class TransactionListRecordBuilder(AbstractRecordBuilder):
    def __init__(self):
        super().__init__()


class TransactionListRecord(AbstractRecord):
    def __init__(self):
        super().__init__()
        # Primary Key
        self.user = None
        self.txn_type = None
        self.bits = Decimal("0")
        self.usdt = Decimal("0")
        self.price = Decimal("0")
        self.bits_before_txn = None
        self.bits_after_txn = None
        self.usdt_before_txn = None
        self.usdt_after_txn = None
        self.extension_info = None