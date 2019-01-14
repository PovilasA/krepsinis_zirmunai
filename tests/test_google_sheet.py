from krepsinis_zirmunai import google_client as gc
from krepsinis_zirmunai import google_sheet as gs

from mock import call, MagicMock
import pytest
from pytest_mock import mocker 

from tests.run_online_tests import *
import random


client = gc.Pygsheets().authenticate().get_client()
test_spreadsheet_name ='krepsinis_zirmunai_test_spreadsheet'

def create_test_spreadsheet():
   spreadsheet = client.create(test_spreadsheet_name)
   worksheet = spreadsheet.worksheet_by_title('Sheet1')
   worksheet.cell('B1').value = 'value_B1'
   worksheet.cell('B2').value = 2
   return(spreadsheet, worksheet)


def delete_test_spreadsheet():
   client.open(test_spreadsheet_name).delete()


def mock_gs_worksheet(mocker):
   spreadsheet_mock = MagicMock()
   worksheet_mock = MagicMock()

   mocker.patch.object(client, 'open')
   client.open.return_value = spreadsheet_mock

   mocker.patch.object(spreadsheet_mock, 'worksheet_by_title')
   spreadsheet_mock.worksheet_by_title.return_value = worksheet_mock

   return(spreadsheet_mock, worksheet_mock)
   

### __init__

def test_initialization_saves_input(mocker):
   spreadsheet_mock, worksheet_mock = mock_gs_worksheet(mocker)
   wks = gs.Worksheet(client, 'spreadsheet_name', 'worksheet_name')
   assert isinstance(wks.client, gc.pygsheets.client.Client)
   assert spreadsheet_mock == wks.spreadsheet
   assert worksheet_mock == wks.worksheet

def test_initialization_catches_SpreadsheetNotFound_error(mocker):
   if RUN_ONLINE_TESTS: 
      # Random names for spreadsheet and worksheet to ensure (almost 100%)
      # that there are no such documents created in reality.
      random.seed(1)
      name1 = ''.join(random.choice('ABCDEFGHIJKLMNOP') for i in range(16))
      name2 = ''.join(random.choice('ABCDEFGHIJKLMNOP') for i in range(16))
      with pytest.raises(gs.GoogleSpreadsheetNotFound):
         gs.Worksheet(client, name1, name2)

   # Offline test
   mocker.patch.object(client, 'open')
   client.open.side_effect = gc.pygsheets.SpreadsheetNotFound()
   with pytest.raises(gs.GoogleSpreadsheetNotFound):
       gs.Worksheet(client, 'spreadsheet_name', 'worksheet_name')

def test_initialization_catches_WorksheetNotFound_error(mocker):
   if RUN_ONLINE_TESTS: 
      spreadsheet, worksheet = create_test_spreadsheet()
      random.seed(2)
      name2 = ''.join(random.choice('ABCDEFGHIJKLMNOP') for i in range(16))
      with pytest.raises(gs.GoogleWorksheetNotFound):
         gs.Worksheet(client, test_spreadsheet_name, name2)
      delete_test_spreadsheet()

   # Offline test
   spreadsheet_mock = MagicMock()
   worksheet_mock = MagicMock()

   mocker.patch.object(client, 'open')
   client.open.return_value = spreadsheet_mock

   mocker.patch.object(spreadsheet_mock, 'worksheet_by_title')
   spreadsheet_mock.worksheet_by_title.side_effect = gc.pygsheets.WorksheetNotFound()

   with pytest.raises(gs.GoogleWorksheetNotFound):
       gs.Worksheet(client, 'spreadsheet_name', 'worksheet_name')


### read_cell()

def test_read_value_returns_correct_value_of_the_cell(mocker):
   if RUN_ONLINE_TESTS:
      _,_ = create_test_spreadsheet()
      wks = gs.Worksheet(client, test_spreadsheet_name, 'Sheet1')
      assert wks.read_cell('B1') == 'value_B1'
      delete_test_spreadsheet()

   # Offline test
   _, worksheet_mock = mock_gs_worksheet(mocker)
   cell_mock = MagicMock()
   mocker.patch.object(worksheet_mock, 'cell')
   worksheet_mock.cell.return_value = cell_mock
   mocker.patch.object(cell_mock, 'value')
   cell_mock.value = 'value_B1'

   wks = gs.Worksheet(client, 'spreadsheet_name', 'worksheet_name')
   assert wks.read_cell('B1') == 'value_B1'

