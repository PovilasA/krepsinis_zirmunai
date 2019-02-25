from krepsinis_zirmunai import google_client as gc
from krepsinis_zirmunai import google_sheet as gs

import pytest

from tests.run_online_tests import *
from tests.helpers.helper_methods import *
from tests.helpers.mocks import *
import random

client = gc.Pygsheets().authenticate().get_client()

### __init__

def test_initialization_saves_input(mocker):
   spreadsheet_mock, worksheet_mock = mock_gs_worksheet(client, mocker)
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
      create_test_spreadsheet(client)
      random.seed(2)
      name2 = ''.join(random.choice('ABCDEFGHIJKLMNOP') for i in range(16))
      with pytest.raises(gs.GoogleWorksheetNotFound):
         gs.Worksheet(client, test_spreadsheet_name, name2)
      delete_test_spreadsheet(client)

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
      _,_ = create_test_spreadsheet(client)
      wks = gs.Worksheet(client, test_spreadsheet_name, 'Sheet1')
      assert wks.read_cell('B1') == 'value_B1'
      delete_test_spreadsheet(client)

   # Offline test
   _, worksheet_mock = mock_gs_worksheet(client, mocker)
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
      _,_ = create_test_spreadsheet(client)
      wks = gs.Worksheet(client, test_spreadsheet_name, 'Sheet1')
      wks_range = wks.Range('A1:C2')

      assert wks_range.pygsheets_worksheet == wks.worksheet
      assert wks_range.spreadsheet_name == test_spreadsheet_name
      assert wks_range.worksheet_name == 'Sheet1'

      m = wks_range.raw_matrix
      assert_range_matrix_class(m, gc.pygsheets.cell.Cell)
      delete_test_spreadsheet(client)

   # Offline test
   worksheet_mock = mock_gs_range(client, mocker)
   wks = gs.Worksheet(client, test_spreadsheet_name, 'Sheet1')
   wks_range = wks.Range('A1:C2')
   assert isinstance(wks_range, gs.Worksheet._Range)
   assert wks_range.pygsheets_worksheet == worksheet_mock
   assert wks_range.spreadsheet_name == 'spreadsheet_title'
   assert wks_range.worksheet_name == 'worksheet_title'
   assert wks_range.string_range == 'A1:C2'
   assert_range_matrix_class(wks_range.new_matrix, FakePygsheetsCell)
   assert_range_matrix_class(wks_range.raw_matrix, FakePygsheetsCell)
   wks.worksheet.range.assert_called_with('A1:C2', 'cells')

### extract methods (tested only some final methods. Others are very similar)

#### PrepareTable as_matrix

def test_get_cells_matrix_without_headers_without_indices(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range(client)
      m = wks_range.get_cells_matrix(headers=False, indices=False)
      assert_range_matrix_class(m, gc.pygsheets.cell.Cell)
      delete_test_spreadsheet(client)

   # Offline test
   mock_gs_range(client, mocker)
   wks_range = create_range(client)
   m = wks_range.get_cells_matrix(headers=False, indices=False)
   assert_range_matrix_class(m, FakePygsheetsCell)

def test_get_values_matrix_with_headers_with_indices(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range(client,'A1:B2', named_index=False)
      m = wks_range.get_values_matrix(headers=True, indices=True)
      assert m == [['2']]
      delete_test_spreadsheet(client)

   # Offline test
   mock_gs_range(client, mocker, matrix_dim = [2,2])
   wks_range = create_range(client, 'A1:B2', named_index=False)
   m = wks_range.get_values_matrix(headers=True, indices=True)
   assert m == [['no_value']]

#### PrepareTable as_dataframe

def test_get_colors_dataframe_with_header_with_indices(mocker):
   if RUN_ONLINE_TESTS:
      wks_range =create_range(client, named_index=True)
      df = wks_range.get_colors_dataframe(headers=True, indices=True)
      tupl = (None, None, None, None)
      df_test = gs.pd.DataFrame([[tupl,tupl,tupl]], columns = [(1, 1, 0, 0),tupl,tupl]).set_index((1, 1, 0, 0))
      gs.pd.testing.assert_frame_equal(df, df_test)
      delete_test_spreadsheet(client)

   # Offline test
   mock_gs_range(client, mocker)
   wks_range =create_range(client, named_index=True)
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
      wks_range = create_range(client, named_index=False)
      df = wks_range.get_colors_dataframe(headers=True, indices=False)
      tupl = (None, None, None, None)
      df_test = gs.pd.DataFrame([[tupl,tupl,tupl]], columns = [tupl]*3)
      gs.pd.testing.assert_frame_equal(df, df_test)
      delete_test_spreadsheet(client)

   # Offline test
   mock_gs_range(client, mocker)
   wks_range = create_range(client)
   df = wks_range.get_colors_dataframe(headers=True, indices=False)
   tupl = (0, 1, 0, 0)
   df_test = gs.pd.DataFrame([[tupl,tupl,tupl]], columns = [tupl]*3)
   gs.pd.testing.assert_frame_equal(df, df_test)


def test_get_values_dataframe_without_headers_with_indices(mocker):
   if RUN_ONLINE_TESTS:
      wks_range =create_range(client, named_index=True)
      df = wks_range.get_values_dataframe(headers=False, indices=True)
      df_test = gs.pd.DataFrame({1:['value_B1','2'],2:['','']}, index=['index_name','1'])
      gs.pd.testing.assert_frame_equal(df, df_test)
      delete_test_spreadsheet(client)

   # Offline test
   mock_gs_range(client, mocker)
   wks_range = create_range(client)
   df = wks_range.get_values_dataframe(headers=False, indices=True)
   df_test = gs.pd.DataFrame({1:['no_value','no_value'],
                              2:['no_value','no_value']}, 
                             index=['no_value','no_value'])
   gs.pd.testing.assert_frame_equal(df, df_test)


def test_get_cells_dataframe_without_header_without_indices(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range(client, named_index=False)
      df = wks_range.get_cells_dataframe(headers=False, indices=False)
      assert list(df.columns) == [0,1,2]
      assert list(df.index) == [0,1]
      m = [[item for item in row] for _,row in df.iterrows()]
      assert_range_matrix_class(m, gc.pygsheets.cell.Cell)
      delete_test_spreadsheet(client)

   # Offline test
   mock_gs_range(client, mocker)
   wks_range = create_range(client)
   df = wks_range.get_cells_dataframe(headers=False, indices=False)
   assert list(df.columns) == [0,1,2]
   assert list(df.index) == [0,1]
   m = [[item for item in row] for _,row in df.iterrows()]
   assert_range_matrix_class(m, FakePygsheetsCell)


def test_unhashable_objects_cannot_be_extracted_as_dataframe_headers(mocker):
   # CellExtract().default or cell object is only example so far
   if RUN_ONLINE_TESTS:
      wks_range = create_range(client, named_index=False)
      with pytest.raises(gs.Worksheet._Range.PrepareTableError):
         wks_range.get_cells_dataframe(headers=True, indices=True)
      delete_test_spreadsheet(client)
   
   # Offline test
   mock_gs_range(client, mocker)
   wks_range = create_range(client, named_index=False)
   with pytest.raises(gs.Worksheet._Range.PrepareTableError):
      wks_range.get_cells_dataframe(headers=True, indices=True)


# Extractions class methods are obvious and not tested

#### ParseTable

def test_raise_error_if_table_is_not_matrix_or_dataframe(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range(client)
      table = [1,2,3] # list but not list of lists
      with pytest.raises(gs.Worksheet._Range.ParseTableError):
         wks_range.change_values(table)
      delete_test_spreadsheet(client)   
   
   # Offline test
   mock_gs_range(client, mocker)
   wks_range = create_range(client)
   table = [1,2,3] # list but not list of lists
   with pytest.raises(gs.Worksheet._Range.ParseTableError):
      wks_range.change_values(table)

def test_raise_error_when_matrix_elements_are_not_equal_length(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range(client)
      table = [[1,2,3],[1,2]] # list of lists but not equal lengths
      with pytest.raises(gs.Worksheet._Range.ParseTableError):
         wks_range.change_values(table)
      delete_test_spreadsheet(client)   
   
   # Offline test
   mock_gs_range(client, mocker)
   wks_range = create_range(client)
   table = [[1,2,3],[1,2]] # list of lists but not equal lengths
   with pytest.raises(gs.Worksheet._Range.ParseTableError):
      wks_range.change_values(table)

def test_raise_error_when_table_dimensions_does_not_fit_raw_matrix(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range(client)
      table = [[1,2],[1,2]] # list of lists but dimensions not equal to raw_matrix dimensions
      with pytest.raises(gs.Worksheet._Range.ParseTableError):
         wks_range.change_values(table, headers=False, indices=False)
      delete_test_spreadsheet(client)

   # Offline test
   mock_gs_range(client, mocker)
   wks_range = create_range(client)
   table = [[1,2],[1,2]] # list of lists but dimensions not equal to raw_matrix dimensions
   with pytest.raises(gs.Worksheet._Range.ParseTableError):
      wks_range.change_values(table, headers=False, indices=False)

#### ParseTable from_matrix

def test_change_cells_from_matrix_without_headers_without_indices(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range(client)
      table = [[FakePygsheetsCell()]*3]*2
      wks_range.change_cells(table, headers=False, indices=False)
      assert_range_matrix_class(wks_range.new_matrix, FakePygsheetsCell)
      delete_test_spreadsheet(client)

   # Offline test
   mock_gs_range(client, mocker)
   wks_range = create_range(client)
   table = [[FakePygsheetsCell()]*3]*2
   wks_range.change_cells(table, headers=False, indices=False)
   assert_range_matrix_class(wks_range.new_matrix, FakePygsheetsCell)

def test_change_values_from_matrix_with_headers_with_indices(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range(client)
      table = [['header','header','header','header'],
               ['11','12','13','14'],['21','22','23','24']]
      wks_range.change_values(table, headers=True, indices=True)
      new_values = [[x_ij.value for x_ij in x_i] for x_i in wks_range.new_matrix]
      assert_range_matrix_class(wks_range.new_matrix, gc.pygsheets.cell.Cell)
      assert new_values == [['12','13','14'],['22','23','24']]
      delete_test_spreadsheet(client)

   # Offline test
   mock_gs_range(client, mocker)
   wks_range = create_range(client)
   table = [['header','header','header','header'],
            ['11','12','13','14'],['21','22','23','24']]
   wks_range.change_values(table, headers=True, indices=True)
   new_values = [[x_ij.value for x_ij in x_i] for x_i in wks_range.new_matrix]
   assert_range_matrix_class(wks_range.new_matrix, FakePygsheetsCell)
   assert new_values == [['12','13','14'],['22','23','24']]
 
#### ParseTable from_dataframe

def test_change_values_from_dataframe_with_headers_with_indices(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range(client)
      table = gs.pd.DataFrame({'header1':['11','21'],
                              'header2':['12','22'],
                              'header3':['13','23']})
      wks_range.change_values(table, headers=True, indices=True)
      new_values = [[x_ij.value for x_ij in x_i] for x_i in wks_range.new_matrix]
      assert_range_matrix_class(wks_range.new_matrix, gc.pygsheets.cell.Cell)
      assert new_values == [['11','12','13'],['21','22','23']]
      delete_test_spreadsheet(client)

   # Offline test
   mock_gs_range(client, mocker)
   wks_range = create_range(client)
   table = gs.pd.DataFrame({'header1':['11','21'],
                            'header2':['12','22'],
                            'header3':['13','23']})
   wks_range.change_values(table, headers=True, indices=True)
   new_values = [[x_ij.value for x_ij in x_i] for x_i in wks_range.new_matrix]
   assert_range_matrix_class(wks_range.new_matrix, FakePygsheetsCell)
   assert new_values == [['11','12','13'],['21','22','23']]

def test_change_values_from_dataframe_with_headers_without_indices(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range(client)
      table = gs.pd.DataFrame({'index':['11','21'],
                               'header2':['12','22'],
                               'header3':['13','23']}).set_index('index')
      wks_range.change_values(table, headers=True, indices=False)
      new_values = [[x_ij.value for x_ij in x_i] for x_i in wks_range.new_matrix]
      assert_range_matrix_class(wks_range.new_matrix, gc.pygsheets.cell.Cell)
      assert new_values == [['11','12','13'],['21','22','23']]
      delete_test_spreadsheet(client)

   # Offline test
   mock_gs_range(client,mocker)
   wks_range = create_range(client)
   table = gs.pd.DataFrame({'index':['11','21'],
                            'header2':['12','22'],
                            'header3':['13','23']}).set_index('index')
   wks_range.change_values(table, headers=True, indices=False)
   new_values = [[x_ij.value for x_ij in x_i] for x_i in wks_range.new_matrix]
   assert_range_matrix_class(wks_range.new_matrix, FakePygsheetsCell)
   assert new_values == [['11','12','13'],['21','22','23']]

def test_change_colors_from_dataframe_without_headers_with_indices(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range(client)
      color = lambda x: (x/100, 1, 0, 0)
      table = gs.pd.DataFrame({color(1):[color(11)],
                              color(2):[color(12)],
                              color(3):[color(13)]})
      wks_range.change_colors(table, headers=False, indices=True)
      new_colors = [[x_ij.color for x_ij in x_i] for x_i in wks_range.new_matrix]
      assert_range_matrix_class(wks_range.new_matrix, gc.pygsheets.cell.Cell)
      assert new_colors == [[color(1),color(2),color(3)],[color(11),color(12),color(13)]]
      delete_test_spreadsheet(client)

   # Offline test
   mock_gs_range(client,mocker)
   wks_range = create_range(client)
   color = lambda x: (x/100, 1, 0, 0)
   table = gs.pd.DataFrame({color(1):[color(11)],
                            color(2):[color(12)],
                            color(3):[color(13)]})
   wks_range.change_colors(table, headers=False, indices=True)
   new_colors = [[x_ij.color for x_ij in x_i] for x_i in wks_range.new_matrix]
   assert_range_matrix_class(wks_range.new_matrix, FakePygsheetsCell)
   assert new_colors == [[color(1),color(2),color(3)],[color(11),color(12),color(13)]]

def test_change_values_from_dataframe_without_headers_without_indices(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range(client)
      table = gs.pd.DataFrame({'header1':['11'],
                              'header2':['12'],
                              'header3':['13']}).set_index('header1')
      wks_range.change_values(table, headers=False, indices=False)
      new_values = [[x_ij.value for x_ij in x_i] for x_i in wks_range.new_matrix]
      assert_range_matrix_class(wks_range.new_matrix, gc.pygsheets.cell.Cell)
      assert new_values == [['header1','header2','header3'],['11','12','13']]
      delete_test_spreadsheet(client)

   # Offline test
   mock_gs_range(client, mocker)
   wks_range = create_range(client)
   table = gs.pd.DataFrame({'header1':['11'],
                            'header2':['12'],
                            'header3':['13']}).set_index('header1')
   wks_range.change_values(table, headers=False, indices=False)
   new_values = [[x_ij.value for x_ij in x_i] for x_i in wks_range.new_matrix]
   assert_range_matrix_class(wks_range.new_matrix, FakePygsheetsCell)
   assert new_values == [['header1','header2','header3'],['11','12','13']]

#### change Returns self (_Range object)

def test_change_method_returns_Range_object(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range(client)
      table = [[1,2,3],[1,2,3]]
      result = wks_range.change('raw_value',headers=False, indices=False, table=table)
      assert isinstance(result, gs.Worksheet._Range)
      delete_test_spreadsheet(client)

   # Offline test
   mock_gs_range(client, mocker)
   wks_range = create_range(client)
   table = [[1,2,3],[1,2,3]]
   result = wks_range.change('raw_value',headers=False, indices=False, table=table)
   assert isinstance(result, gs.Worksheet._Range)

def test_raw_matrix_is_unchanged_after_change_is_called(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range(client)
      table = [[1,2,3],[1,2,3]]
      old_values = [[x_ij.value for x_ij in x_i] for x_i in wks_range.raw_matrix]
      wks_range.change('raw_value',headers=False, indices=False, table=table)
      new_values = [[x_ij.value for x_ij in x_i] for x_i in wks_range.raw_matrix]
      assert new_values == [['index_name', 'value_B1', ''], ['1', '2', '']]
      assert old_values == new_values
      delete_test_spreadsheet(client)

   # Offline test
   mock_gs_range(client, mocker)
   wks_range = create_range(client)
   # cheat to make raw_matrix and new_matrix different objects
   import copy; wks_range.new_matrix = copy.deepcopy(wks_range.raw_matrix)
   table = [[1,2,3],[1,2,3]]
   old_values = [[x_ij.value for x_ij in x_i] for x_i in wks_range.raw_matrix]
   wks_range.change('raw_value',headers=False, indices=False, table=table)
   new_values = [[x_ij.value for x_ij in x_i] for x_i in wks_range.raw_matrix]
   assert new_values == [['no_value']*3]*2
   assert old_values == new_values

def test_second_change_does_not_override_first_change(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range(client)
      values_table = gs.pd.DataFrame({'header1':['11','21'],
                                        'header2':['12','22'],
                                        'header3':['13','23']})
      wks_range.change_values(values_table, headers=True, indices=True)
      color = lambda x: (x/100, 1, 0, 0)
      colors_table = gs.pd.DataFrame({color(1):[color(11),color(21)],
                              color(2):[color(12),color(22)],
                              color(3):[color(13),color(23)]})
      wks_range.change_colors(colors_table, headers=True, indices=True)
      new_values = [[x_ij.value for x_ij in x_i] for x_i in wks_range.new_matrix]
      new_colors = [[x_ij.color for x_ij in x_i] for x_i in wks_range.new_matrix]
      assert new_values == [['11','12','13'],['21','22','23']]
      assert new_colors == [[color(11),color(12),color(13)],
                            [color(21),color(22),color(23)]]
      delete_test_spreadsheet(client)

   # Offline test
   mock_gs_range(client, mocker)
   wks_range = create_range(client)
   values_table = gs.pd.DataFrame({'header1':['11','21'],
                                    'header2':['12','22'],
                                    'header3':['13','23']})
   wks_range.change_values(values_table, headers=True, indices=True)
   color = lambda x: (x/100, 1, 0, 0)
   colors_table = gs.pd.DataFrame({color(1):[color(11),color(21)],
                           color(2):[color(12),color(22)],
                           color(3):[color(13),color(23)]})
   wks_range.change_colors(colors_table, headers=True, indices=True)
   new_values = [[x_ij.value for x_ij in x_i] for x_i in wks_range.new_matrix]
   new_colors = [[x_ij.color for x_ij in x_i] for x_i in wks_range.new_matrix]
   assert new_values == [['11','12','13'],['21','22','23']]
   assert new_colors == [[color(11),color(12),color(13)],
                        [color(21),color(22),color(23)]]

#### set_changes THIS TEST IS TEMPORARY USELESS. 
# UNTIL TODO IN set_changes() WILL BE DONE

def test_set_changes(mocker):
   if RUN_ONLINE_TESTS:
      wks_range = create_range(client)
      values_table = gs.pd.DataFrame({'header1':['11','21'],
                                        'header2':['12','22'],
                                        'header3':['13','23']})
      wks_range.change_values(values_table, headers=True, indices=True)
      color = lambda x: (x/100, 1, 0, 0)
      colors_table = gs.pd.DataFrame({color(1):[color(20),color(40)],
                              color(2):[color(60),color(80)],
                              color(3):[color(0),color(100)]})
      wks_range.change_colors(colors_table, headers=True, indices=True)
      wks_range.set_changes()
      updated_worksheet = gs.Worksheet(client, test_spreadsheet_name, 'Sheet1')
      updated_range = updated_worksheet.Range('A1:C2')
      updated_values = [[x_ij.value for x_ij in x_i] for x_i in updated_range.raw_matrix]
      updated_colors = [[x_ij.color for x_ij in x_i] for x_i in updated_range.raw_matrix]
      assert updated_values == [['11','12','13'],['21','22','23']]
      assert updated_colors == [[color(20),color(60),color(0)],
                                [color(40),color(80),color(100)]]
      delete_test_spreadsheet(client)
   # Offline test
   # TODO when TODO in set_changes() will be done
