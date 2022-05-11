import abc
import datetime
import logging
import typing
from typing import Type, Union

from dataclasses_json import dataclass_json

from XTBClient.models.models import ConnectionMode, Symbol, Calendar, CurrentUserData, Trade, RateInfo, Transaction, TransactionStatus, \
    XTBDataClass
from XTBClient.models.requests import ChartLastInfoRecord, ChartRangeRecord, LoginRequest


class XTBBaseClient(abc.ABC):
    def __init__(self, user: str, password: str, mode: ConnectionMode, automatic_logout = True, url: str = "wss://ws.xtb.com/", custom_tag: str = "python-xtb-api"):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.url = url
        self.mode = mode
        self.login_request = LoginRequest(user, password)
        self.stream_session_id = None  # used for streaming calls, we get it after a successful login
        self.automatic_logout = automatic_logout

        self.custom_tag = custom_tag
        self.logged_in = False

    def _process_rates(self, rates: list[RateInfo], digits: int):
        # Price values must be divided by 10 to the power of digits in order to obtain exact prices.
        multiplier = 10 ** digits
        for candidate in rates:
            candidate.open /= multiplier
            candidate.close = candidate.open + candidate.close / multiplier
            candidate.high = candidate.open + candidate.high / multiplier
            candidate.low = candidate.open + candidate.low / multiplier
        return rates

    def _parse_response(self, response: dict, result_type: Union[Type[dataclass_json], typing.List[dataclass_json]], data_key: str):
        if result_type:
            data = response[data_key]

            # check if we have a list of something as result
            if typing.get_origin(result_type) == list:
                # if we have a list of elements, convert them with marshmallow schema
                args = typing.get_args(result_type)
                return args[0].schema().load(data, many=True)
            elif issubclass(result_type, XTBDataClass):
                # if it's one of our data types convert it with dataclasses-json
                return result_type.from_dict(data)
            elif isinstance(data, dict):
                # if data type is "normal" value/class like float, int, etc
                return data[list(data.keys())[0]]  # first item in dict, hackish
            else:
                return data  # simple data type here, just return it

        return None

    @abc.abstractmethod
    def login(self) -> None:
        pass

    @abc.abstractmethod
    def logout(self) -> None:
        pass

    @abc.abstractmethod
    def get_all_symbols(self) -> list[Symbol]:
        pass

    @abc.abstractmethod
    def get_calendar(self) -> list[Calendar]:
        pass

    @abc.abstractmethod
    def get_current_user_data(self) -> CurrentUserData:
        pass

    @abc.abstractmethod
    def get_symbol(self, symbol: str) -> Symbol:
        pass

    @abc.abstractmethod
    def get_trades(self, opened_only: bool) -> list[Trade]:
        pass

    @abc.abstractmethod
    def get_trades_history(self, start: datetime.datetime = datetime.datetime.fromtimestamp(0), end: datetime.datetime = datetime.datetime.fromtimestamp(0)) -> list[Trade]:
        pass

    @abc.abstractmethod
    def get_chart_last_request(self, chart_info: ChartLastInfoRecord) -> list[RateInfo]:
        pass

    @abc.abstractmethod
    def get_chart_range_request(self, chart_range: ChartRangeRecord) -> list[RateInfo]:
        pass

    @abc.abstractmethod
    def trade_transaction(self, transaction: Transaction) -> int:
        pass

    @abc.abstractmethod
    def transaction_status(self, transaction_id: int) -> TransactionStatus:
        pass
