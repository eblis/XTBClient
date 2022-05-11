import pytest

from tests import testing_utils


@pytest.mark.asyncio
async def test_get_trades(mocker):
    async with testing_utils.mock_xtb_client(mocker) as client:
        testing_utils.mock_next_client_response(client, mocker, "tests/data/get_trades.json")
        trades = await client.get_trades(False)
        assert trades
