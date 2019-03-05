from krepsinis_zirmunai.statistics.individual_summary import *

from tests.helpers.mocks import *

parsed_input = read_mock_table('parsed_input_table.csv', format='dataframe')
ind_summary = IndividualSummary(parsed_input)

def test_values_compute():
   ind_summary_values = ind_summary.Values().compute()
   values_correct = individual_summary_values()
   assert ind_summary_values.equals(values_correct)

def test_notes_compute():
   ind_summary_notes = ind_summary.Notes().compute()
   notes_correct = individual_summary_notes()
   assert ind_summary_notes == notes_correct
