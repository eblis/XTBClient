import datetime
import decimal
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import dataclasses_json
from dataclasses_json import dataclass_json, LetterCase, config, Undefined, DataClassJsonMixin
from marshmallow import fields
from marshmallow.fields import DateTime


def guarded_datetime_2_milliseconds_encoder(date: datetime.datetime):
    val = date if not date or isinstance(date, int) else date.timestamp()
    return int(val * 1000) if val else val


def guarded_datetime_2_milliseconds_decoder(millis):
    return datetime.datetime.utcfromtimestamp(millis / 1000.0) if millis is not None else millis


dataclasses_json.cfg.global_config.encoders[datetime.datetime] = guarded_datetime_2_milliseconds_encoder
dataclasses_json.cfg.global_config.decoders[datetime.datetime] = guarded_datetime_2_milliseconds_decoder

dataclasses_json.cfg.global_config.encoders[Optional[datetime.datetime]] = guarded_datetime_2_milliseconds_encoder
dataclasses_json.cfg.global_config.decoders[Optional[datetime.datetime]] = guarded_datetime_2_milliseconds_decoder


class XTBDateTime(fields.DateTime):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.DESERIALIZATION_FUNCS["timestamp_ms"] = guarded_datetime_2_milliseconds_decoder
        self.SERIALIZATION_FUNCS["timestamp_ms"] = guarded_datetime_2_milliseconds_encoder

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return value
        elif value == 0:
            return None

        return super(DateTime, self)._deserialize(value, attr, data, **kwargs)

    def _serialize(self, value, **kwargs):
        return guarded_datetime_2_milliseconds_encoder(value)

# register marshmallow datetime serialization and deserialization
# add a new format called timestamp_ms

@dataclass
class XTBDataClass(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)["dataclasses_json"]

    def default(self, unknown):
        print(unknown)


class XTBCommand(Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    GET_ALL_SYMBOLS = "getAllSymbols"
    GET_CALENDAR = "getCalendar"
    GET_CURRENT_USER_DATA = "getCurrentUserData"
    GET_SYMBOL = "getSymbol"
    GET_TRADES = "getTrades"
    GET_TRADES_HISTORY = "getTradesHistory"
    GET_CHART_LAST_REQUEST = "getChartLastRequest"
    GET_CHART_RANGE_REQUEST = "getChartRangeRequest"
    TRADE_TRANSACTION = "tradeTransaction"
    TRANSACTION_STATUS = "tradeTransactionStatus"


class ConnectionMode(Enum):
    REAL = "real"
    DEMO = "demo"


class Period(Enum):
    PERIOD_M1 = 1       # 1 minute
    PERIOD_M5 = 5       # 5 minutes
    PERIOD_M15 = 15     # 15 minutes
    PERIOD_M30 = 30     # 30 minutes
    PERIOD_H1 = 60      # 60 minutes (1 hour)
    PERIOD_H4 = 240     # 240 minutes (4 hours)
    PERIOD_D1 = 1440    # 1440 minutes (1 day)
    PERIOD_W1 = 10080   # 10080 minutes (1 week)
    PERIOD_MN1 = 43200  # 43200 minutes (30 days)


class TradeOperation(Enum):
    Buy = 0
    Sell = 1
    Buy_Limit = 2
    Sell_Limit = 3
    Buy_Stop = 4
    Sell_stop = 5
    Balance = 6
    Credit = 7


class TradeType(Enum):
    Open = 0  # order open, used for opening orders
    Pending = 1  # order pending, only used in the streaming getTrades  command
    Close = 2  # order close
    Modify = 3  # order modify, only used in the tradeTransaction  command
    Delete = 4  # order delete, only used in the tradeTransaction  command


@dataclass
class ApiCommand(XTBDataClass):
    command: XTBCommand
    custom_tag: Optional[str] = field(default=None, metadata=config(exclude=lambda f: f is None))  # don't include custom_tag if null
    arguments: Optional[dataclass_json] = field(default=None, metadata=config(exclude=lambda f: f is None))  # don't include arguments if null
    pretty_print: bool = True


class QuoteId(Enum):
    Fixed = 1
    Float = 2
    Depth = 3
    Cross = 4
    Unknown_5 = 5
    Unknown_6 = 6


class MarginMode(Enum):
    Forex = 101
    CFD_Leveraged = 102
    CFD = 103
    Unknown = 104


class ProfitMode(Enum):
    Forex = 5
    CFD = 6


class RequestStatus(Enum):
    Error = 0
    Pending = 1
    Accepted = 3
    Rejected = 4


@dataclass
class Symbol(XTBDataClass):
    ask: float  # Ask price in base currency
    bid: float  # Bid price in base currency
    category_name: str  # Category name
    contract_size: int  # Size of 1 lot
    currency: str  # Currency
    currency_pair: bool  # Indicates whether the symbol represents a currency pair
    currency_profit: str  # The currency of calculated profit
    description: str  # Description
    group_name: str  # Symbol group name
    high: float  # The highest price of the day in base currency
    initial_margin: int  # Initial margin for 1 lot order, used for profit/margin calculation
    instant_max_volume: int  # Maximum instant volume multiplied by 100 (in lots)
    leverage: float  # Symbol leverage
    long_only: bool  # Long only
    lot_max: float  # Maximum size of trade
    lot_min: float  # Minimum size of trade
    lot_step: float  # A value of minimum step by which the size of trade can be changed (within lotMin - lotMax range)
    low: float  # The lowest price of the day in base currency
    margin_hedged: int  # Used for profit calculation
    margin_hedged_strong: bool  # For margin calculation
    margin_maintenance: int  # For margin calculation, null if not applicable
    margin_mode: MarginMode  # For margin calculation
    percentage: float  # Percentage
    pips_precision: int  # Number of symbol's pip decimal places
    precision: int  # Number of symbol's price decimal places
    profit_mode: ProfitMode  # For profit calculation
    quote_id: QuoteId  # Source of price
    short_selling: bool  # Indicates whether short selling is allowed on the instrument
    spread_raw: float  # the difference between raw ask and bid prices
    spread_table: float  # Spread representation
    step_rule_id: int  # Appropriate step rule ID from getStepRules  command response
    stops_level: int  # Minimal distance (in pips) from the current price where the stopLoss/takeProfit can be set
    swap_rollover3days: int = field(metadata=config(field_name="swap_rollover3days"))  # Time when additional swap is accounted for weekend
    swap_enable: bool  # Indicates whether swap value is added to position on end of day
    swap_long: float  # Swap value for long positions in pips
    swap_short: float  # Swap value for short positions in pips
    swap_type: int  # Type of swap calculated
    symbol: str  # Symbol name
    time_string: str  # Time in string
    trailing_enabled: bool  # Indicates whether trailing stop (offset) is applicable to the instrument.
    type: int  # Instrument class number

    expiration: Optional[datetime.datetime] = field(default=None, metadata=config(mm_field=XTBDateTime(allow_none=True, format="timestmap_ms")))  # Null if not applicable
    starting: Optional[datetime.datetime] = field(default=None, metadata=config(mm_field=XTBDateTime(allow_none=True, format="timestmap_ms")))  # Null if not applicable
    tick_size: Optional[float] = None  # Smallest possible price change, used for profit/margin calculation, null if not applicable
    tick_value: Optional[float] = None  # Value of smallest possible price change (in base currency), used for profit/margin calculation, null if not applicable
    time: Optional[datetime.datetime] = field(default=None,
        metadata=config(mm_field=XTBDateTime(allow_none=True, format='timestamp_ms')))  # Ask & bid tick time


@dataclass
class Calendar(XTBDataClass):
    country: str  # Two letter country code
    current: str  # Market value (current), empty before time of release of this value (time from "time" record)
    forecast: str  # Forecasted value
    impact: str  # Impact on market
    period: str  # Information period
    previous: str  # Value from previous information release
    title: str  # Name of the indicator for which values will be released

    time: Optional[datetime.datetime] = field(default=None,
        metadata=config(mm_field=XTBDateTime(format='timestamp_ms')))  # Time, when the information will be released (in this time empty "current" value should be changed with exact released value)


@dataclass
class CurrentUserData(XTBDataClass):
    company_unit: int  # Unit the account is assigned to.
    currency: str  # account currency
    group: str  # group
    ib_account: bool  # Indicates whether this account is an IB account.
    # leverage: int  # This field should not be used. It is inactive and its value is always 1.
    leverage_multiplier: float  # The factor used for margin calculations. The actual value of leverage can be calculated by dividing this value by 100.
    trailing_stop: bool  # 	Indicates whether this account is enabled to use trailing stop.

    spread_type: Optional[str] = None  # spreadType, null if not applicable


@dataclass
class Trade(XTBDataClass):
    close_price: float = field(metadata=config(field_name="close_price"))  # Close price in base currency
    closed: bool  # Closed
    cmd: TradeOperation  # Operation code
    comment: str  # Comment
    commission: float  # Commision in account currency, null if not applicable
    digits: int  # Number of decimal places
    margin_rate: float = field(metadata=config(field_name="margin_rate")) # Margin rate
    offset: int  # Trailing offset
    open_price: float = field(metadata=config(field_name="open_price"))  # Open price in base currency
    open_time: datetime.datetime = field(metadata=config(field_name="open_time", mm_field=XTBDateTime(format='timestamp_ms')))  # Open time
    open_time_string: str = field(metadata=config(field_name="open_timeString"))  # Open time string
    order: int  # Order number for opened transation
    order2: int  # Order number for closed transaction
    position: int  # Order number common both for opened and closed transaction
    profit: float  # Profit in account currency
    sl: float  # Zero if stop loss is not set (in base currency)
    storage: float  # Order swaps in account currency
    timestamp: datetime.date = field(metadata=config(mm_field=XTBDateTime(format='timestamp_ms')))  # Timestamp
    tp: float  # Zero if take profit is not set (in base currency)
    volume: float  # Volume in lots

    custom_comment: Optional[str] = None  # The value the customer may provide in order to retrieve it later.
    close_time: Optional[datetime.datetime] = field(default=None,
        metadata=config(mm_field=XTBDateTime(allow_none=True, format='timestamp_ms')))  # Null if order is not closed
    close_time_string: Optional[str] = field(default=None, metadata=config(field_name="close_timeString"))  # Null if order is not closed
    expiration: Optional[datetime.datetime] = field(default=None,
        metadata=config(mm_field=XTBDateTime(allow_none=True, format='timestamp_ms')))  # Null if order is not closed
    expiration_string: Optional[str] = None  # Null if order is not closed
    symbol: Optional[str] = None  # symbol name or null for deposit/withdrawal operations


@dataclass
class RateInfo(XTBDataClass):
    close: decimal.Decimal  # Value of close price (shift from open price)
    ctm: datetime.datetime = field(metadata=config(mm_field=XTBDateTime(format='timestamp_ms')))  # Candle start time in CET / CEST time zone (see Daylight Saving Time, DST)
    ctm_string: str  # String representation of the 'ctm' field
    high: decimal.Decimal  # Highest value in the given period (shift from open price)
    low: decimal.Decimal  # Lowest value in the given period (shift from open price)
    open: decimal.Decimal  # Open price (in base currency * 10 to the power of digits)
    vol: decimal.Decimal  # Volume in lots


@dataclass
class RateHistory(XTBDataClass):
    digits: int
    rate_infos: list[RateInfo]


@dataclass
class News(XTBDataClass):
    body: str  # Body
    bodylen: int  # Body length
    key: str  # News key
    time: datetime.datetime = field(metadata=config(mm_field=XTBDateTime(format='timestamp_ms')))  # Time
    time_string: str  # Time string
    title: str  # News title


@dataclass
class Transaction(XTBDataClass):
    cmd: TradeOperation  # Operation code
    expiration: datetime.datetime = field(metadata=config(mm_field=XTBDateTime(format='timestamp_ms')))  # Pending order expiration time
    offset: int  # Trailing offset
    price: float  # Trade price
    sl: float  # Stop loss
    symbol: str  # Trade symbol
    tp: float  # Take profit
    type: TradeType  # Trade transaction type
    volume: float  # Trade volume

    custom_comment: Optional[str] = None  # The value the customer may provide in order to retrieve it later.
    order: Optional[int] = 0  # 0 or position number for closing/modifications


@dataclass
class TransactionStatus(XTBDataClass):
    ask: float  # Price in base currency
    bid: float  # Price in base currency
    order: int  # Unique order number
    request_status: RequestStatus  # Request status code

    custom_comment: Optional[str] = None  # The value the customer may provide in order to retrieve it later.
    message: Optional[str] = None  # Can be null
