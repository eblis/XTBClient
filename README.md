# XTBClient

> X-Trade Brokers (XTB) trading platform client, supporting both asynchronous and synchronous clients with typed classes.

A python library supporting both asyncio and "normal" clients for X-Trade Brokers (XTB) trading using websockets.

It will use either [websockets](https://websockets.readthedocs.io/en/stable/) if using the [async XTB client](XTBClient/client/axtb.py) or [websocket-client](https://websocket-client.readthedocs.io/en/latest/) if using the [sync XTB client](XTBClient/client/xtb.py)

# Source code
Available on [github.com](https://github.com/eblis/XTBClient)

# Installing
To install the client(s) just run `pip install xtb-client`.
Or, better yet, using poetry run `poetry add xtb-client`.

# Getting started
Both clients support context manager notation  - `with` or `async with` statement.

## Async client
If you call the API too quicky the server may disconnect you so I've added some `sleep` calls to simulate waiting a bit.

```python
import asyncio
import datetime
import logging
import sys

from XTBClient.client import XTBAsyncClient
from XTBClient.models.models import ConnectionMode, Period, Transaction, TradeOperation, TradeType
from XTBClient.models.requests import ChartLastInfoRecord, ChartRangeRecord

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)


async def async_client_test(user, password):
    logger = logging.getLogger("async client")

    async with XTBAsyncClient(user, password, mode=ConnectionMode.DEMO) as client:
        start = datetime.datetime.now()
        future = start.replace(year=start.year + 1)
        start = start.replace(year=start.year - 1)

        transaction = Transaction(
            cmd=TradeOperation.Buy,
            custom_comment="Testing custom comment",
            expiration=future,
            offset=0,
            order=0,
            price=1.12,
            sl=0.0,
            symbol="EURUSD",
            tp=0.0,
            type=TradeType.Open,
            volume=1
        )

        id = await client.trade_transaction(transaction)
        logger.info(f"Initiated transaction: {id}")

        status = await client.transaction_status(id)
        logger.info(f"Trade transaction status: {status}")

        chart_info = await client.get_chart_last_request(ChartLastInfoRecord(Period.PERIOD_M5, datetime.datetime.now(), "EURPLN"))
        logger.info(f"Last chart info: {chart_info}")

        chart_info = await client.get_chart_range_request(
            ChartRangeRecord(Period.PERIOD_M5, datetime.datetime.utcnow(), datetime.datetime.now(), "EURPLN", ticks=5))
        logger.info(f"Chart range info: {chart_info}")

        trades = await client.get_trades(False)
        logger.info(f"All trades: {trades}")

        trades = await client.get_trades_history(start=start, end=datetime.datetime.now())
        logger.info(f"All trades history: {trades}")

        await asyncio.sleep(1)

        eurpln = await client.get_symbol("EURPLN")
        logger.info(f"EURO -> PLN: {eurpln}")

        current_user = await client.get_current_user_data()
        logger.info(f"Current user: {current_user}")

        calendars = await client.get_calendar()
        logger.info(f"All calendars: {calendars}")

        await asyncio.sleep(1)

        symbols = await client.get_all_symbols()
        logger.info(f"All symbols: {symbols}")


asyncio.get_event_loop().run_until_complete(async_client_test("user", "password"))
```

## Sync (normal) client
If you call the API too quicky the server may disconnect you so I've added some `sleep` calls to simulate waiting a bit.

```python
import datetime
import logging
import sys
import time

from XTBClient.models.models import ConnectionMode, Period, Transaction, TradeOperation, TradeType
from XTBClient.models.requests import ChartLastInfoRecord, ChartRangeRecord
from XTBClient.client.xtb import XTBSyncClient

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)


def sync_client_test(user, password):
    logger = logging.getLogger("sync client")

    with XTBSyncClient(user, password, mode=ConnectionMode.DEMO, proxy=None) as client:
        start = datetime.datetime.now()
        future = start.replace(year=start.year + 1)
        start = start.replace(year=start.year - 1)

        transaction = Transaction(
            cmd=TradeOperation.Buy,
            custom_comment="Testing custom comment",
            expiration=future,
            offset=0,
            order=0,
            price=1.12,
            sl=0.0,
            symbol="EURUSD",
            tp=0.0,
            type=TradeType.Open,
            volume=1
        )

        id = client.trade_transaction(transaction)
        logger.info(f"Initiated transaction: {id}")

        status = client.transaction_status(id)
        logger.info(f"Trade transaction status: {status}")

        chart_info = client.get_chart_last_request(ChartLastInfoRecord(Period.PERIOD_M5, datetime.datetime.now(), "EURPLN"))
        logger.info(f"Last chart info: {chart_info}")

        chart_info = client.get_chart_range_request(
            ChartRangeRecord(Period.PERIOD_M5, datetime.datetime.utcnow(), datetime.datetime.now(), "EURPLN", ticks=5))
        logger.info(f"Chart range info: {chart_info}")

        trades = client.get_trades(False)
        logger.info(f"All trades: {trades}")

        trades = client.get_trades_history(start=start, end=datetime.datetime.now())
        logger.info(f"All trades history: {trades}")

        time.sleep(1)

        eurpln = client.get_symbol("EURPLN")
        logger.info(f"EURO -> PLN: {eurpln}")

        current_user = client.get_current_user_data()
        logger.info(f"Current user: {current_user}")

        calendars = client.get_calendar()
        logger.info(f"All calendars: {calendars}")

        time.sleep(1)

        symbols = client.get_all_symbols()
        logger.info(f"All symbols: {symbols}")


sync_client_test("user", "password")
```

# API and usage
Since this is Python you can browse through the code to find out what methods are available and how to use them.
All methods and classes should have typing hints so you can tell what each method expects as parameters.

**All return types from the XTB API is typed, there's no dictionaries with unknown key/value pairs or anything similar.**

# Working on the code
This project uses poetry for dependency management as well as for it's publishing functionality.
To get started all you need to do is:
  - open a command prompt
  - clone the repository
  - browse to the newly cloned repository in the already opened command prompt
  - run `poetry install`


# Work in progress
 - Streaming operations like `getCandles` and others are missing
 - Add missing *normal* API methods
 - More unit tests could be added
 - Better documentation
 - Added library to PyPi repository