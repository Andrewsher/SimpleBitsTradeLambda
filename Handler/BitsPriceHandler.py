import decimal
from datetime import datetime
from decimal import Decimal
# import ccxt

from Dao.UserListDao import UserListDao
from Dao.TransactionListDao import TransactionListDao

from Model.UserListRecord import UserListRecord
from Model.UserListRecord import UserListRecordBuilder

class BitsPriceHandler():

    START_PROCESS_LOG = "[{}] Start to process message {}"
    WARN_PROCRESS_LOG = "[{}] WARN: {}"
    ERROR_PROCESS_LOG = "[{}] Failed to process message {} with error {}"
    CREATE_USER_MODE = "CREATE_USER"
    CLOSE_USER_MODE = "CLOSE_USER"
    CALCULATE_PROFIT_MODE = "CALCULATE_PROFIT"
    DEFAULT_MODE = "DEFAULT"

    def __int__(self):
        self.user_list_dao = UserListDao()
        self.txn_list_dao = TransactionListDao()
        self.user_record = None
        self.mode = None

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
                self.__calculate_profit(event)
            else:
                self.__trigger_transaction(event)
        except Exception as e:
            print(BitsPriceHandler.ERROR_PROCESS_LOG.format(
                datetime.utcnow().isoformat(),
                event,
                e
            ))

        # exchange = ccxt.binance() # TODO: refine parameters
        # symbol = 'BTC/USDT'
        # # 获取当前价格
        # price = Decimal(exchange.fetch_ticker(symbol)['last'])
        price = Decimal("12345")
        if self.__buy_signal(price):
            self.__buy(price)
        elif self.sell_signal(price):
            self.__sell(price)

    def __create_user(self, event):
        user_list_with_same_name = self.user_list_dao.query(event["user"])
        if "Items" in user_list_with_same_name and user_list_with_same_name["Items"]:
            print(BitsPriceHandler.WARN_PROCRESS_LOG.format(
                datetime.utcnow().isoformat(),
                f"user {event['user']} already exists, please user another user name"
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

    def __buy_signal(self, price):
        return True

    def __buy(self, price):
        # do something
        pass
    def __sell(self, price):
        pass