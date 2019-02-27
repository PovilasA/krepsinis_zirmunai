from krepsinis_zirmunai.statistics.individual_summary import *

from tests.helpers.mocks import *

parsed_input = read_mock_table('parsed_input_table.csv', format='dataframe')
ind_summary = IndividualSummary(parsed_input)

def test_values_compute():
   ind_summary_values = ind_summary.Values().compute()
   ind_summary_values_correct = individual_summary_values()
   assert ind_summary_values.equals(ind_summary_values_correct)
