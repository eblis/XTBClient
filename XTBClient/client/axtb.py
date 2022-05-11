import datetime
import json
import typing
from typing import Type, Optional, Union

import websockets
from dataclasses_json import dataclass_json

from XTBClient.errors import NotLoggedInError, InvalidCall
from XTBClient.models.models import ConnectionMode, ApiCommand, XTBCommand, Symbol, Calendar, CurrentUserData, Trade, RateHistory, \
    RateInfo, Transaction, TransactionStatus
from XTBClient.models.requests import SymbolRequest, TradesRequest, TradesHistoryRequest, ChartLastInfoRecord, ChartLastRequest, ChartRangeRecord, \
    TransactionRequest, TransactionStatusRequest
from XTBClient.xtb_base import XTBBaseClient


class XTBAsyncClient(XTBBaseClient):
    def __init__(self, user: str, password: str, mode: ConnectionMode, automatic_logout=True, url: str = "wss://ws.xtb.com/", custom_tag: str = "python-xtb-api"):
        super().__init__(user, password, mode, automatic_logout, url, custom_tag)

    async def _send_message_logged_in(self, command: XTBCommand, payload: Optional[dataclass_json], result_type: Type[dataclass_json]) -> Type[dataclass_json]:
        if not self.logged_in:
            raise NotLoggedInError("Must log in first")

        try:
            return await self._send_message(command, payload, result_type)
        except Exception as ex:
            self.logger.exception(f"Error while calling command {command}")
            raise ex  # re-raise for now

    async def _send_message(self, command: XTBCommand, payload: Optional[dataclass_json], result_type: Union[Type[dataclass_json], typing.List[dataclass_json]], data_key="returnData"):
        return await self._send_raw_message(command, payload, result_type, data_key)

    async def _send_raw_message(self, command: XTBCommand, payload: Optional[dataclass_json], result_type: Union[Type[dataclass_json], typing.List[dataclass_json]], data_key):
        # the command we want to send
        self.logger.debug(f"Sending {command} command")  # we don't want to log everything, just the command .. maybe there's some sensitive data involved
        cmd = ApiCommand(command=command, arguments=payload, custom_tag=self.custom_tag)

        raw = cmd.to_json()
        # this will probably not work on on a multi-threaded environment, or where multiple co-routines send and receive data
        # need to investigate this further
        await self.xtb_session.send(raw)  # send command
        res = await self.xtb_session.recv()  # wait for response
        raw = json.loads(res)
        assert raw["customTag"] == self.custom_tag, f"Custom tag doesn't match {self.custom_tag}"

        if raw["status"]:
            return self._parse_response(raw, result_type, data_key)
        else:
            # try both errorDesc and errorDescr
            desc = raw.get("errorDesc", "")
            if not desc:
                desc = raw.get("errorDescr", "")
            raise InvalidCall(raw["errorCode"] + ". " + desc)

    async def login(self) -> None:
        self.stream_session_id = await self._send_message(XTBCommand.LOGIN, self.login_request, str, data_key="streamSessionId")
        self.logged_in = True

    async def logout(self) -> None:
        await self._send_message(XTBCommand.LOGOUT, None, None)
        self.logged_in = False
        self.stream_session_id = None

    async def __aenter__(self):
        self.xtb_session = await websockets.connect(f"{self.url}/{self.mode.value}", max_size=None)  # async web socket

        self.logger.debug("Entering async_client context manager")
        if not self.logged_in:
            await self.login()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.logger.debug("Exiting async_client context manager")
        if self.logged_in and self.automatic_logout:
            await self.logout()
        if self.xtb_session:
            await self.xtb_session.close()
            self.xtb_session = None
        return self

    async def get_all_symbols(self) -> list[Symbol]:
        return await self._send_message_logged_in(XTBCommand.GET_ALL_SYMBOLS, None, list[Symbol])

    async def get_calendar(self) -> list[Calendar]:
        return await self._send_message_logged_in(XTBCommand.GET_CALENDAR, None, list[Calendar])

    async def get_current_user_data(self) -> CurrentUserData:
        return await self._send_message_logged_in(XTBCommand.GET_CURRENT_USER_DATA, None, CurrentUserData)

    async def get_symbol(self, symbol: str) -> Symbol:
        return await self._send_message_logged_in(XTBCommand.GET_SYMBOL, SymbolRequest(symbol), Symbol)

    async def get_trades(self, opened_only: bool) -> list[Trade]:
        return await self._send_message_logged_in(XTBCommand.GET_TRADES, TradesRequest(opened_only), list[Trade])

    async def get_trades_history(self, start: datetime.datetime = datetime.datetime.fromtimestamp(0), end: datetime.datetime = datetime.datetime.fromtimestamp(0)) -> list[Trade]:
        return await self._send_message_logged_in(XTBCommand.GET_TRADES_HISTORY, TradesHistoryRequest(start=start, end=end), list[Trade])

    async def get_chart_last_request(self, chart_info: ChartLastInfoRecord) -> list[RateInfo]:
        # low, high and open are converted to "correct" values in the return object
        data = await self._send_message_logged_in(XTBCommand.GET_CHART_LAST_REQUEST, ChartLastRequest(chart_info), RateHistory)
        return self._process_rates(data.rate_infos, data.digits)

    async def get_chart_range_request(self, chart_range: ChartRangeRecord) -> list[RateInfo]:
        # low, high and open are converted to "correct" values in the return object
        data = await self._send_message_logged_in(XTBCommand.GET_CHART_RANGE_REQUEST, ChartLastRequest(chart_range), RateHistory)
        return self._process_rates(data.rate_infos, data.digits)

    async def trade_transaction(self, transaction: Transaction) -> int:
        return await self._send_message_logged_in(XTBCommand.TRADE_TRANSACTION, TransactionRequest(transaction), int)

    async def transaction_status(self, transaction_id: int) -> TransactionStatus:
        return await self._send_message_logged_in(XTBCommand.TRANSACTION_STATUS, TransactionStatusRequest(transaction_id), TransactionStatus)