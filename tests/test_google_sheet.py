from krepsinis_zirmunai import google_client as gc
from krepsinis_zirmunai import google_sheet as gs

from mock import call, MagicMock
import pytest
from pytest_mock import mocker 

from tests.run_online_tests import *
import random


client = gc.Pygsheets().authenticate().get_client()
test_spreadsheet_name ='krepsinis_zirmunai_test_spreadsheet'

def create_test_spreadsheet(named_index=False):
   spreadsheet = client.create(test_spreadsheet_name)
   worksheet = spreadsheet.worksheet_by_title('Sheet1')
   worksheet.cell('B1').value = 'value_B1'
   worksheet.cell('B2').value = 2
   worksheet.cell('A2').value = 1
   if named_index:
      worksheet.cell('A1').value = 'index_name'
      worksheet.cell('A1').color = (1, 1, 0, 0)
   return(spreadsheet, worksheet)


def delete_test_spreadsheet():
   client.open(test_spreadsheet_name).delete()


def mock_gs_worksheet(mocker):
   spreadsheet_mock = MagicMock()
   worksheet_mock = MagicMock()

   mocker.patch.object(client, 'open')
   client.open.return_value = spreadsheet_mock

   mocker.patch.object(client, 'create')
   client.create.return_value = spreadsheet_mock

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
   assert wks_range.new_matrix == None
   assert_range_matrix_class(wks_range.raw_matrix, FakePygsheetsCell)
   wks.worksheet.range.assert_called_with('A1:C2', 'cells')

### extract methods (tested only some final methods. Others are very similar)

def assert_range_matrix_class(matrix, cell_class):
   assert len(matrix) == 2
   assert len(matrix[0]) == 3
   assert len(matrix[1]) == 3
   assert all(isinstance(x, cell_class) for x in matrix[0])
   assert all(isinstance(x, cell_class) for x in matrix[1])

def create_range(string_range = 'A1:C2', named_index='False'):
   _,_ = create_test_spreadsheet(named_index=named_index)
   wks = gs.Worksheet(client, test_spreadsheet_name, 'Sheet1')
   wks_range = wks.Range(string_range)
   return(wks_range)

class FakePygsheetsCell:
   def __init__(self, value='no_value', color=(0, 1, 0, 0)):
      self.value = value
      self.color = color
      self.__hash__ = None

def mock_gs_range(mocker, matrix_dim = [2,3]):
   spreadsheet_mock, worksheet_mock = mock_gs_worksheet(mocker)
   mocker.patch.object(worksheet_mock, 'range')
   mocker.patch.object(worksheet_mock, 'title')
   mocker.patch.object(spreadsheet_mock, 'title')
   worksheet_mock.range.return_value = [[FakePygsheetsCell() for x_ij in range(matrix_dim[1])] 
                                         for x_i in range(matrix_dim[0])]
   worksheet_mock.title = 'worksheet_title'
   spreadsheet_mock.title = 'spreadsheet_title'
   return(worksheet_mock)
   
#### PrepareTable as_matrix

def test_get_cells_matrix_without_headers_without_indices(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range()
      m = wks_range.get_cells_matrix(headers=False, indices=False)
      assert_range_matrix_class(m, gc.pygsheets.cell.Cell)
      delete_test_spreadsheet()

   # Offline test
   mock_gs_range(mocker)
   wks_range = create_range()
   m = wks_range.get_cells_matrix(headers=False, indices=False)
   assert_range_matrix_class(m, FakePygsheetsCell)

def test_get_values_matrix_with_headers_with_indices(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range('A1:B2', named_index=False)
      m = wks_range.get_values_matrix(headers=True, indices=True)
      assert m == [['2']]
      delete_test_spreadsheet()

   # Offline test
   mock_gs_range(mocker, matrix_dim = [2,2])
   wks_range = create_range('A1:B2', named_index=False)
   m = wks_range.get_values_matrix(headers=True, indices=True)
   assert m == [['no_value']]

#### PrepareTable as_dataframe

def test_get_colors_dataframe_with_header_with_indices(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range(named_index=True)
      df = wks_range.get_colors_dataframe(headers=True, indices=True)
      tupl = (None, None, None, None)
      df_test = gs.pd.DataFrame([[tupl,tupl,tupl]], columns = [(1, 1, 0, 0),tupl,tupl]).set_index((1, 1, 0, 0))
      gs.pd.testing.assert_frame_equal(df, df_test)
      delete_test_spreadsheet()

   # Offline test
   mock_gs_range(mocker)
   wks_range = create_range(named_index=True)
   wks_range.raw_matrix[0][0] = FakePygsheetsCell(color=(1, 1, 0, 0)) # mock index name value
   wks_range.raw_matrix[1][0] = FakePygsheetsCell(color=(1, 1, 0, 0)) # don't know exactly why this value is automatically the same as [0][0]
   df = wks_range.get_colors_dataframe(headers=True, indices=True)
   tupl = (0, 1, 0, 0)
   df_test = gs.pd.DataFrame([[(1, 1, 0, 0),tupl,tupl]], 
                             columns = [(1, 1, 0, 0),tupl,tupl]
                             ).set_index((1, 1, 0, 0))
   gs.pd.testing.assert_frame_equal(df, df_test)

def test_get_colors_dataframe_with_headers_without_indices(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range(named_index=False)
      df = wks_range.get_colors_dataframe(headers=True, indices=False)
      tupl = (None, None, None, None)
      df_test = gs.pd.DataFrame([[tupl,tupl,tupl]], columns = [tupl]*3)
      gs.pd.testing.assert_frame_equal(df, df_test)
      delete_test_spreadsheet()

   # Offline test
   mock_gs_range(mocker)
   wks_range = create_range()
   df = wks_range.get_colors_dataframe(headers=True, indices=False)
   tupl = (0, 1, 0, 0)
   df_test = gs.pd.DataFrame([[tupl,tupl,tupl]], columns = [tupl]*3)
   gs.pd.testing.assert_frame_equal(df, df_test)


def test_get_values_dataframe_without_headers_with_indices(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range(named_index=True)
      df = wks_range.get_values_dataframe(headers=False, indices=True)
      df_test = gs.pd.DataFrame({1:['value_B1','2'],2:['','']}, index=['index_name','1'])
      gs.pd.testing.assert_frame_equal(df, df_test)
      delete_test_spreadsheet()

   # Offline test
   mock_gs_range(mocker)
   wks_range = create_range()
   df = wks_range.get_values_dataframe(headers=False, indices=True)
   df_test = gs.pd.DataFrame({1:['no_value','no_value'],
                              2:['no_value','no_value']}, 
                             index=['no_value','no_value'])
   gs.pd.testing.assert_frame_equal(df, df_test)


def test_get_cells_dataframe_without_header_without_indices(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range(named_index=False)
      df = wks_range.get_cells_dataframe(headers=False, indices=False)
      assert list(df.columns) == [0,1,2]
      assert list(df.index) == [0,1]
      m = [[item for item in row] for _,row in df.iterrows()]
      assert_range_matrix_class(m, gc.pygsheets.cell.Cell)
      delete_test_spreadsheet()

   # Offline test
   mock_gs_range(mocker)
   wks_range = create_range()
   df = wks_range.get_cells_dataframe(headers=False, indices=False)
   assert list(df.columns) == [0,1,2]
   assert list(df.index) == [0,1]
   m = [[item for item in row] for _,row in df.iterrows()]
   assert_range_matrix_class(m, FakePygsheetsCell)


def test_unhashable_objects_cannot_be_extracted_as_dataframe_headers(mocker):
   # CellExtract().default or cell object is only example so far
   if RUN_ONLINE_TESTS:
      wks_range = create_range(named_index=False)
      with pytest.raises(gs.Worksheet._Range.PrepareTableError):
         wks_range.get_cells_dataframe(headers=True, indices=True)
      delete_test_spreadsheet()
   
   # Offline test
   mock_gs_range(mocker)
   wks_range = create_range(named_index=False)
   with pytest.raises(gs.Worksheet._Range.PrepareTableError):
      wks_range.get_cells_dataframe(headers=True, indices=True)


# Extractions class methods are obvious and not tested

#### ParseTable

def test_raise_error_if_table_is_not_matrix_or_dataframe(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range()
      table = [1,2,3] # list but not list of lists
      with pytest.raises(gs.Worksheet._Range.ParseTableError):
         wks_range.change_values(table)
      delete_test_spreadsheet()   
   
   # Offline test
   mock_gs_range(mocker)
   wks_range = create_range()
   table = [1,2,3] # list but not list of lists
   with pytest.raises(gs.Worksheet._Range.ParseTableError):
      wks_range.change_values(table)

def test_raise_error_when_matrix_elements_are_not_equal_length(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range()
      table = [[1,2,3],[1,2]] # list of lists but not equal lengths
      with pytest.raises(gs.Worksheet._Range.ParseTableError):
         wks_range.change_values(table)
      delete_test_spreadsheet()   
   
   # Offline test
   mock_gs_range(mocker)
   wks_range = create_range()
   table = [[1,2,3],[1,2]] # list of lists but not equal lengths
   with pytest.raises(gs.Worksheet._Range.ParseTableError):
      wks_range.change_values(table)

def test_raise_error_when_table_dimensions_does_not_fit_raw_matrix(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range()
      table = [[1,2],[1,2]] # list of lists but dimensions not equal to raw_matrix dimensions
      with pytest.raises(gs.Worksheet._Range.ParseTableError):
         wks_range.change_values(table, headers=False, indices=False)
      delete_test_spreadsheet()

   # Offline test
   mock_gs_range(mocker)
   wks_range = create_range()
   table = [[1,2],[1,2]] # list of lists but dimensions not equal to raw_matrix dimensions
   with pytest.raises(gs.Worksheet._Range.ParseTableError):
      wks_range.change_values(table, headers=False, indices=False)

#### ParseTable from_matrix

def test_change_cells_from_matrix_without_headers_without_indices(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range()
      table = [[FakePygsheetsCell()]*3]*2
      wks_range.change_cells(table, headers=False, indices=False)
      assert_range_matrix_class(wks_range.new_matrix, FakePygsheetsCell)
      delete_test_spreadsheet()

   # Offline test
   mock_gs_range(mocker)
   wks_range = create_range()
   table = [[FakePygsheetsCell()]*3]*2
   wks_range.change_cells(table, headers=False, indices=False)
   assert_range_matrix_class(wks_range.new_matrix, FakePygsheetsCell)

def test_change_values_from_matrix_with_headers_with_indices(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range()
      table = [['header','header','header','header'],
               ['11','12','13','14'],['21','22','23','24']]
      wks_range.change_values(table, headers=True, indices=True)
      new_values = [[x_ij.value for x_ij in x_i] for x_i in wks_range.new_matrix]
      assert_range_matrix_class(wks_range.new_matrix, gc.pygsheets.cell.Cell)
      assert new_values == [['12','13','14'],['22','23','24']]
      delete_test_spreadsheet()

   # Offline test
   mock_gs_range(mocker)
   wks_range = create_range()
   table = [['header','header','header','header'],
            ['11','12','13','14'],['21','22','23','24']]
   wks_range.change_values(table, headers=True, indices=True)
   new_values = [[x_ij.value for x_ij in x_i] for x_i in wks_range.new_matrix]
   assert_range_matrix_class(wks_range.new_matrix, FakePygsheetsCell)
   assert new_values == [['12','13','14'],['22','23','24']]
 
#### ParseTable from_dataframe

def test_change_values_from_dataframe_with_header_with_indices(mocker):
   assert 1==2

def test_change_values_from_dataframe_with_headers_without_indices(mocker):
   assert 1==2

def test_change_colors_from_dataframe_without_headers_with_indices(mocker):
   assert 1==2

def test_change_cells_from_dataframe_without_header_without_indices(mocker):
   assert 1==2