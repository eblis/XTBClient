import datetime
from dataclasses import dataclass, field
from typing import Union

from dataclasses_json import config

from XTBClient.models.models import XTBDataClass, Period, XTBDateTime, Transaction


@dataclass
class LoginRequest(XTBDataClass):
    user_id: str
    password: str


@dataclass
class SymbolRequest(XTBDataClass):
    symbol: str


@dataclass
class TradesRequest(XTBDataClass):
    opened_only: bool


@dataclass
class TradesHistoryRequest(XTBDataClass):
    start: datetime.datetime
    end: datetime.datetime


@dataclass
class ChartLastInfoRecord(XTBDataClass):
    period: Period  # Period code
    start: datetime.datetime = field(metadata=config(mm_field=XTBDateTime(format='timestamp_ms')))  # Start of chart block (rounded down to the nearest interval and excluding)
    symbol: str  # Symbol


@dataclass
class ChartRangeRecord(XTBDataClass):
    period: Period  # Period code
    start: datetime.datetime = field(metadata=config(mm_field=XTBDateTime(format='timestamp_ms')))  # Start of chart block (rounded down to the nearest interval and excluding)
    end: datetime.datetime = field(metadata=config(mm_field=XTBDateTime(format='timestamp_ms')))  # End of chart block (rounded down to the nearest interval and excluding)
    symbol: str  # Symbol
    """
Ticks field - if ticks is not set or value is 0, getChartRangeRequest  works as before (you must send valid start and end time fields).
If ticks value is not equal to 0, field end is ignored.
If ticks >0 (e.g. N) then API returns N candles from time start.
If ticks <0 then API returns N candles to time start.
It is possible for API to return fewer chart candles than set in tick field.
    """
    ticks: int = None  # Number of ticks needed, this field is optional, please read the description above


@dataclass
class ChartLastRequest(XTBDataClass):
    info: Union[ChartLastInfoRecord, ChartRangeRecord]


@dataclass
class TransactionRequest(XTBDataClass):
    tradeTransInfo: Transaction

@dataclass
class TransactionStatusRequest(XTBDataClass):
    order: int