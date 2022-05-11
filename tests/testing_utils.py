import json
from pathlib import Path

from XTBApi.client.axtb import XTBAsyncClient
from XTBApi.models.models import ConnectionMode, XTBCommand, XTBDataClass, ApiCommand


def mock_xtb_client(mocker, login_successful=True) -> XTBAsyncClient:
    instance = XTBAsyncClient("test_user", "test_password", ConnectionMode.DEMO, url="", automatic_logout=False)  # make sure url isn't going anywhere
    instance.__websocket = mocker.patch("websockets.connect", new=mocker.AsyncMock())  # save our websocket mocked instance, just in case
    instance.logged_in = login_successful

    return instance


def get_test_file_data(file_name) -> str:
    with Path(file_name).open() as fin:
        return fin.read()


def mock_next_client_response(client, mocker, file_name):
    data = get_test_file_data(file_name)
    full = '{"status": true, "customTag": "' + client.custom_tag + '", "returnData": ' + data + ' }'

    client.xtb_session.recv = mocker.AsyncMock(return_value=full)
    return client


def assert_command_sent(client: XTBAsyncClient, command: XTBCommand, payload: XTBDataClass):
    cmd = ApiCommand(command=command, arguments=payload, custom_tag=client.custom_tag)
    raw = cmd.to_json()

    client.xtb_session.send.assert_called_with(raw)


def mock_fail_next_client_response(client, mocker, error_code, error_description):
    data = {"status": False, "errorCode": error_code, "errorDesc": error_description, "customTag": client.custom_tag}
    client.xtb_session.recv = mocker.AsyncMock(return_value=json.dumps(data))
    return client
