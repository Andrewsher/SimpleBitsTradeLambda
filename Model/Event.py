from decimal import Decimal
class Event:
    def __init__(
            self,
            user: str,
            mode: str,
            currency: str = None,
            init_usdt: Decimal = None
    ):
        """
        Construction method of Event
        :param user: str, required, user name
        :param mode: str, required, how Lambda will handle this event. Should be one of CREATE_USER, CLOSE_USER, CALCULATE_PROFIT and TRIGGER_TRANSACTION
        :param currency: str, optional, the currency of digital coin, required only when mode='CREATE_USER
        :param init_usdt: decimal, optional, required only when mode='CREATE_USER'
        """
        self.user: str = user
        self.mode: str = mode
        self.currency: str = currency
        self.init_usdt: Decimal = init_usdt
