from krepsinis_zirmunai import google_client as gc

from mock import MagicMock
import pandas as pd
import csv


def mock_gs_worksheet(client, mocker):
   spreadsheet_mock = MagicMock()
   worksheet_mock = MagicMock()

   mocker.patch.object(client, 'open')
   client.open.return_value = spreadsheet_mock

   mocker.patch.object(client, 'create')
   client.create.return_value = spreadsheet_mock

   mocker.patch.object(spreadsheet_mock, 'worksheet_by_title')
   spreadsheet_mock.worksheet_by_title.return_value = worksheet_mock

   return(spreadsheet_mock, worksheet_mock)


class FakePygsheetsCell:
   def __init__(self, value='no_value', color=(0, 1, 0, 0)):
      self.value = value
      self.color = color
      self.__hash__ = None

def mock_gs_range(client, mocker, matrix_dim = [2,3]):
   spreadsheet_mock, worksheet_mock = mock_gs_worksheet(client, mocker)
   mocker.patch.object(worksheet_mock, 'range')
   mocker.patch.object(worksheet_mock, 'title')
   mocker.patch.object(spreadsheet_mock, 'title')
   worksheet_mock.range.return_value = [[FakePygsheetsCell() for x_ij in range(matrix_dim[1])] 
                                         for x_i in range(matrix_dim[0])]
   worksheet_mock.title = 'worksheet_title'
   spreadsheet_mock.title = 'spreadsheet_title'
   return(worksheet_mock)

def assert_range_matrix_class(matrix, cell_class):
   assert len(matrix) == 2
   assert len(matrix[0]) == 3
   assert len(matrix[1]) == 3
   assert all(isinstance(x, cell_class) for x in matrix[0])
   assert all(isinstance(x, cell_class) for x in matrix[1])

def read_mock_table(file_name, format='matrix'):
   with open('tests/statistics/helper_tables/' + file_name, 'r') as f:
      reader = csv.reader(f)
      matrix = list(reader)
   matrix = [item[0].replace('ļ»æ','').split(';') for item in matrix]
   if format == 'matrix':
      return(matrix)
   elif format == 'dataframe':
      headers = matrix[0][1:] 
      rows = [v[0] for v in matrix][1:]
      matrix = [v[1:] for v in matrix]
      matrix = matrix[1:]
      df = pd.DataFrame(matrix, columns=headers, index=rows)
      df = df.apply(pd.to_numeric, errors='coerce')
      return(df)

def mock_read_input_data(mocker, read_input_data_object):
   values = read_mock_table('raw_statistics_example_values.csv')
   colors = read_mock_table('raw_statistics_example_colors.csv')
   read_input_data_object.values_matrix = values
   read_input_data_object.colors_matrix = colors
   return(read_input_data_object)

def individual_summary_values():
   values = [
      [23,'7 - 2','+115','DWWWW','DWWWW','+92','Nepralaimėjo 5','Nepralaimėjo 5'],
      [13,'3 - 2','+29', 'D--LW','DLWLW','+9', 'Lygiosios 1','Nelaimėjo 2'],
      [10,'1 - 1','-7', 'D----','DWLDD','-7', 'Lygiosios 1','Nepralaimėjo 2'],
      [17,'1 - 5','-48','DL-LW','DLLWL','-18','Nelaimėjo 2','Nelaimėjo 3'],
      [9, '7 - 2','+80','-LWW-','LWWWW','+64', 'Nebuvo 1','Pralaimėjo 1'],
      [6, '1 - 5','-81','-LL-L','LLLWL','-71','Nebuvo 1','Pralaimėjo 3'],
      [15,'3 - 3','-5', '-W-L-','WLLLW','-22','Nebuvo 1','Laimėjo 1'],
      [19,'3 - 6','-58','-LLW-','LLWWL','-42','Nebuvo 1','Pralaimėjo 2'],
      [17,'5 - 2','+46','-WW-L','WWLWW','+39', 'Nebuvo 1','Laimėjo 2'],
      [19,'5 - 4','+51','-WWLW','WWLWL','+47', 'Nebuvo 1','Laimėjo 2'],
      [19,'4 - 4','+29','DWWW-','DWWWL','+59', 'Nepralaimėjo 4','Nepralaimėjo 4'],
      [18,'6 - 3','+72','-LW-W','LWWLW','+56', 'Nebuvo 1','Pralaimėjo 1']
   ]

   columns = ['Sužaista','Laimėta-Pralaimėta','Taškų santykis','Paskutiniai 5 kartai','Paskutiniai 5 kartai (be praleidimų)','Taškų santykis per paskutinius 5 kartus','Serija','Serija (be praleidimų)']
   player_names = [
   'Name_one ASurname_one',
   'Name_one BSurname_two',
   'Name_three Surname_three',
   'Name_four Surname_three',
   'Name_five Surname_five',
   'Name_one Surname_six',
   'Name_five Surname_seven',
   'Name_eight Surname_eight',
   'Name_nine Surname_nine',
   'Name_ten Surname_ten',
   'Name_eleven Surname_eleven',
   'Name_twelwe Surname_twelve'
   ]

   return(pd.DataFrame(values, columns=columns, index=player_names))
