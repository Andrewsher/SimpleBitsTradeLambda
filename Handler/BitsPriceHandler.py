from datetime import datetime
from decimal import Decimal
import ccxt

from Dao.UserListDao import UserListDao
from Dao.TransactionRecordDao import TransactionRecordDao

class BitsPriceHandler():

    START_PROCESS_LOG = "[{}] Start to process message {}"

    def __int__(self):
        self.user_list_dao = UserListDao()
        self.txn_record_dao = TransactionRecordDao()
        self.user = None

    def handle_request(self, event: dict):
        print(BitsPriceHandler.START_PROCESS_LOG.format(
            datetime.utcnow().isoformat(),
            event
        ))
        self.user = event["user"]

        exchange = ccxt.binance() # TODO: refine parameters
        symbol = 'BTC/USDT'
        # 获取当前价格
        price = Decimal(exchange.fetch_ticker(symbol)['last'])
        if self.buy_signal(price):
            buy(price)
        elif self.sell_signal(price):
            sell(price)


    def buy_signal(self, price):
        return True

    def buy(self, price):
        # do something
        pass
