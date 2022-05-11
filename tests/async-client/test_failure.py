import pytest

from XTBClient.errors import InvalidCall
from tests import testing_utils


@pytest.mark.asyncio
async def test_call_fails(mocker):
    async with testing_utils.mock_xtb_client(mocker) as client:
        testing_utils.mock_fail_next_client_response(client, mocker, "E123", "Some error description")
        with pytest.raises(InvalidCall):
            failure = await client.login()
