from krepsinis_zirmunai import google_client as gc
from krepsinis_zirmunai import google_sheet as gs

from krepsinis_zirmunai.statistics.read_input_data import *
from krepsinis_zirmunai.statistics.individual_summary import *
from krepsinis_zirmunai.statistics.write_results import *

from tests.helpers.helper_methods import *
from tests.helpers.mocks import *
from tests.run_online_tests import *

client = gc.Pygsheets().authenticate().get_client()
parsed_input = read_mock_table('parsed_input_table.csv', format='dataframe')

def test_execute_with_individual_summary():
   if RUN_ONLINE_TESTS:
      create_test_spreadsheet(client, insert_values = False)
      individual_summary = IndividualSummary(parsed_input)
      WriteResults(client, 'krepsinis_zirmunai_test_spreadsheet', 'Lankomumas',
                   individual_summary).execute()
   
      expected_values = individual_summary_values()
      expected_notes = individual_summary_notes()
      expected_wrap_strategies = individual_summary_wrap_strategies()
      
      worksheet = gs.Worksheet(client, 'krepsinis_zirmunai_test_spreadsheet',
                              'Lankomumas')
      
      range = worksheet.Range('B3:J15')
      actual_values = range.get_values_dataframe(headers=True, indices=True)
      actual_notes = range.get_notes_matrix(headers=False, indices=False)   
      actual_wrap_strategies = range.get_wrap_strategies_matrix(headers=False, indices=False)
      assert actual_values.equals(expected_values)
      assert actual_notes == expected_notes
      assert actual_wrap_strategies == expected_wrap_strategies
      delete_test_spreadsheet(client)

   #TODO maybe to do offline test?
