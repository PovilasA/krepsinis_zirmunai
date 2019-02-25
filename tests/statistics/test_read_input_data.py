from krepsinis_zirmunai import google_client as gc
from krepsinis_zirmunai import google_sheet as gs
from krepsinis_zirmunai.statistics.read_input_data import *

from freezegun import freeze_time

from tests.run_online_tests import *
from tests.helpers.helper_methods import *
from tests.helpers.mocks import *

client = gc.Pygsheets().authenticate().get_client()
test_spreadsheet_name ='krepsinis_zirmunai_test_spreadsheet'

def test_find_string_range(mocker):
   matrix = [['','','','',''],
             ['',11,11,'',''],
             ['','','',11,''],
             [11,'','','',''],
             ['','','','','']]
   assert find_string_range(matrix) == 'A2:D4'

def test_init(mocker):
   if RUN_ONLINE_TESTS:
      _, worksheet = create_test_spreadsheet(client, insert_values=False)
      worksheet.cell('C3').value = 11
      worksheet.cell('D4').value = 11
      worksheet.cell('E5').value = 11
      worksheet.cell('A6').value = 11
      worksheet.cell('C3').color = (1,1,1,0)
      worksheet.cell('D4').color = (1,1,1,0)
      worksheet.cell('E5').color = (1,1,1,0)
      worksheet.cell('A6').color = (1,1,1,0)
      input = ReadInputData(client, test_spreadsheet_name, 'Sheet1')
      assert isinstance(input.worksheet, gs.Worksheet)
      assert input.string_range == 'A3:E6'
      matrix = [['','','11','',''],
                ['','','','11',''],
                ['','','','','11'],
                ['11','','','','']]
      assert input.values_matrix == matrix
      n = (None, None, None, None)
      v = (1, 1, 1, 0)
      matrix = [[n,n,v,n,n],
                [n,n,n,v,n],
                [n,n,n,n,v],
                [v,n,n,n,n]]
      assert input.colors_matrix == matrix
      delete_test_spreadsheet(client)

   # Offline test
   spreadsheet_mock, worksheet_mock = mock_gs_worksheet(client, mocker)
   matrix = [['','','11','',''],
             ['','','','11',''],
             ['','','','','11'],
             ['11','','','','']]
   worksheet_mock.get_all_values.return_value = matrix
   input = ReadInputData(client, test_spreadsheet_name, 'Sheet1')
   assert isinstance(input.worksheet, gs.Worksheet)
   assert input.worksheet.worksheet == worksheet_mock
   assert input.string_range == 'A1:E4'
   assert input.values_matrix == []
   assert input.colors_matrix == []
   assert input.top_values == 12

@freeze_time("2019-02-20")
def test_parse(mocker):
   mock_gs_worksheet(client, mocker)
   input = ReadInputData(client, test_spreadsheet_name, 'Sheet1')
   mock_read_input_data(mocker, input)
   parsed_df = input.parse()
   parsed_df_correct = read_mock_table('parsed_input_table.csv', format='dataframe')
   assert parsed_df.shape == (12,24)
   assert parsed_df.equals(parsed_df_correct)
