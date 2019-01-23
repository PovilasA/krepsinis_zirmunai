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
      create_test_spreadsheet()
      random.seed(2)
      name2 = ''.join(random.choice('ABCDEFGHIJKLMNOP') for i in range(16))
      with pytest.raises(gs.GoogleWorksheetNotFound):
         gs.Worksheet(client, test_spreadsheet_name, name2)
      delete_test_spreadsheet()

   # Offline test
   spreadsheet_mock = MagicMock()

   mocker.patch.object(client, 'open')
   client.open.return_value = spreadsheet_mock

   mocker.patch.object(spreadsheet_mock, 'worksheet_by_title')
   spreadsheet_mock.worksheet_by_title.side_effect = gc.pygsheets.WorksheetNotFound()

   with pytest.raises(gs.GoogleWorksheetNotFound):
       gs.Worksheet(client, 'spreadsheet_name', 'worksheet_name')


### read_cell()

def test_read_cell_returns_correct_value_of_the_cell(mocker):
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

### class Range

def test_Range_function_initialize_Range_class(mocker):
   if RUN_ONLINE_TESTS:
      _,_ = create_test_spreadsheet()
      wks = gs.Worksheet(client, test_spreadsheet_name, 'Sheet1')
      wks_range = wks.Range('A1:C2')

      assert wks_range.pygsheets_worksheet == wks.worksheet
      assert wks_range.spreadsheet_name == test_spreadsheet_name
      assert wks_range.worksheet_name == 'Sheet1'

      m = wks_range.raw_matrix
      assert_range_matrix_class(m, gc.pygsheets.cell.Cell)
      delete_test_spreadsheet()

   # Offline test
   worksheet_mock = mock_gs_range(mocker)

   wks = gs.Worksheet(client, test_spreadsheet_name, 'Sheet1')
   wks_range = wks.Range('A1:C2')
   assert isinstance(wks_range, gs.Worksheet._Range)
   assert wks_range.pygsheets_worksheet == worksheet_mock
   assert wks_range.spreadsheet_name == 'spreadsheet_title'
   assert wks_range.worksheet_name == 'worksheet_title'
   assert wks_range.string_range == 'A1:C2'
   assert_range_matrix_class(wks_range.raw_matrix, FakePygsheetsCell)
   wks.worksheet.range.assert_called_with('A1:C2', 'cells')

### extract methods (tested only some final methods. Others are very similar)

def assert_range_matrix_class(matrix, cell_class):
   assert len(matrix) == 2
   assert len(matrix[0]) == 3
   assert len(matrix[1]) == 3
   assert all(isinstance(x, cell_class) for x in matrix[0])
   assert all(isinstance(x, cell_class) for x in matrix[1])

def create_range():
   _,_ = create_test_spreadsheet()
   wks = gs.Worksheet(client, test_spreadsheet_name, 'Sheet1')
   wks_range = wks.Range('A1:C2')
   return(wks_range)

class FakePygsheetsCell:
   def __init__(self, value='no_value', color='no_color'):
      self.value = value
      self.color = color

def mock_gs_range(mocker):
   spreadsheet_mock, worksheet_mock = mock_gs_worksheet(mocker)
   mocker.patch.object(worksheet_mock, 'range')
   mocker.patch.object(worksheet_mock, 'title')
   mocker.patch.object(spreadsheet_mock, 'title')
   worksheet_mock.range.return_value = [[FakePygsheetsCell()]*3]*2
   worksheet_mock.title = 'worksheet_title'
   spreadsheet_mock.title = 'spreadsheet_title'
   return(worksheet_mock)
   
def test_cells_matrix_without_headers(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range()
      m = wks_range.cells_matrix(headers=False)
      assert_range_matrix_class(m, gc.pygsheets.cell.Cell)
      delete_test_spreadsheet()

   # Offline test
   mock_gs_range(mocker)
   wks_range = create_range()
   m = wks_range.cells_matrix(headers=False)
   assert_range_matrix_class(m, FakePygsheetsCell)

def test_values_dataframe_without_headers(mocker):
   pass

def test_values_matrix_with_headers(mocker):
   pass
   # m = wks_range.values_matrix(True)
   # assert m == [['', '2', '']]

def test_colors_dataframe_with_headers(mocker):
   pass




# Extractions class methods are obvious and not tested