import pytest

from XTBApi.models.models import XTBCommand
from XTBApi.models.requests import SymbolRequest
from tests import testing_utils


@pytest.mark.asyncio
async def test_all_symbols(mocker):
    async with testing_utils.mock_xtb_client(mocker) as client:
        testing_utils.mock_next_client_response(client, mocker, "tests/data/get_all_symbols.json")
        all_symbols = await client.get_all_symbols()
        assert all_symbols

@pytest.mark.asyncio
async def test_single_symbol_list(mocker):
    async with testing_utils.mock_xtb_client(mocker) as client:
        testing_utils.mock_next_client_response(client, mocker, "tests/data/get_all_symbols-small.json")
        all_symbols = await client.get_all_symbols()
        assert all_symbols
        assert len(all_symbols) == 1


@pytest.mark.asyncio
async def test_single_symbol(mocker):
    async with testing_utils.mock_xtb_client(mocker) as client:
        testing_utils.mock_next_client_response(client, mocker, "tests/data/get_symbol.json")
        symbol = await client.get_symbol("BLAH_BLAH")
        testing_utils.assert_command_sent(client, XTBCommand.GET_SYMBOL, SymbolRequest("BLAH_BLAH"))
        assert symbol
