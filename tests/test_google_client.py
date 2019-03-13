from krepsinis_zirmunai import google_client as gc

from mock import call
import pytest

from tests.test_selection import *

def create_client(credentials_file='credentials.json'):
    return(gc.Pygsheets(credentials_file))

### __init__()

def test_initialization():
    # With default credentials file
    client = gc.Pygsheets()
    assert client.credentials_file == 'credentials.json'
    assert client.authentication_completed == False

    # With selected credentials file
    client = create_client('my_credentials.json')
    assert client.credentials_file == 'my_credentials.json'
    assert client.authentication_completed == False

### authenticate()

def test_errors_when_credentials_are_missing(mocker):

    # When both files are missing
    mocker.patch.object(gc.os.path, 'isfile')
    gc.os.path.isfile.return_value = False
    calls = [call('sheets.googleapis.com-python'),
             call('credentials.json')]
    with pytest.raises(gc.PygsheetsClientError):
        create_client().authenticate()
    gc.os.path.isfile.assert_has_calls(calls, any_order=False)


def test_errors_when_pygsheets_authorization_is_not_completed(mocker):

    mocker.patch.object(gc.pygsheets, 'authorize')
    gc.pygsheets.authorize.side_effect = gc.PygsheetsClientError()
    client = create_client()
    with pytest.raises(gc.PygsheetsClientError):
       client.authenticate()
    gc.pygsheets.authorize.assert_called_with(client_secret=client.credentials_file)


def test_set_completed_authentication(mocker):

    mocker.patch.object(gc.os.path, 'isfile')
    gc.os.path.isfile.return_value = True
    mocker.patch.object(gc.pygsheets, 'authorize')
    client = create_client().authenticate()
    assert client.authentication_completed == True 
    
### get_client()

def test_errors_when_client_is_not_authenticated(mocker):
    with pytest.raises(gc.PygsheetsClientError):
       create_client().get_client()

def test_returns_client_when_authentication_is_completed(mocker):
    if RUN_ONLINE_TESTS:
        gc.Pygsheets('credentials.json').authenticate()

    mocker.patch.object(gc.os.path, 'isfile')
    gc.os.path.isfile.return_value = True
    mocker.patch.object(gc.pygsheets, 'authorize')
    gc.pygsheets.authorize.return_value = gc.pygsheets.client.Client('creds')

    client = create_client().authenticate().get_client()
    assert isinstance(client, gc.pygsheets.client.Client)
