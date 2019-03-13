from krepsinis_zirmunai import google_sheet as gs
from krepsinis_zirmunai.statistics.individual_summary import *

class WriteResults:
   def __init__(self, client, spreadsheet_name, worksheet_name, 
                individual_summary=None, individual_summary_string_range='B3:J15'):
   
      self.prepare_worksheet(client, spreadsheet_name, worksheet_name)
      self.worksheet = gs.Worksheet(client, spreadsheet_name, worksheet_name)
      self.individual_summary_string_range = individual_summary_string_range
      self.individual_summary = individual_summary

   def execute(self):
      if self.individual_summary is not None:
         
         values = self.individual_summary.Values().compute()
         notes = self.individual_summary.Notes().compute()
         wrap_strategies = self.individual_summary.WrapStrategies().compute()
         wks_range = self.worksheet.Range(self.individual_summary_string_range)
         wks_range.change_values(values, headers=False, indices=False)
         wks_range.change_notes(notes, headers=False, indices=False)
         wks_range.change_wrap_strategies(wrap_strategies, headers=False, indices=False)
         wks_range.set_changes()
         
         col_widths = self.individual_summary.ColumnWidths()
         col_num_start, col_num_end = get_column_numbers(self.individual_summary_string_range) 
         wks = self.worksheet.worksheet
         for i in range(col_num_start, col_num_end+1):
            wks.adjust_column_width(start=i-1, end=i-1, pixel_size=col_widths[i-col_num_start])
      return True

   def prepare_worksheet(self, client, spreadsheet_name, worksheet_name):
      spreadsheet = client.open(spreadsheet_name)
      if worksheet_name in [wks.title for wks in spreadsheet.worksheets()]:
         # make it empty
         wks = spreadsheet.worksheet_by_title(worksheet_name)
         wks.clear() # to clear not only values: wks.clear(fields='*')
      else:
         # create
         spreadsheet.add_worksheet(worksheet_name)

def get_column_numbers(string_range):
   string_range_splitted = string_range.split(':')
   start_col_letter = ''.join(filter(str.isalpha, string_range_splitted[0]))
   end_col_letter = ''.join(filter(str.isalpha, string_range_splitted[1]))
   return col_to_num(start_col_letter), col_to_num(end_col_letter)

def col_to_num(col_str):
    """ Convert base26 column string to number. """
    expn = 0
    col_num = 0
    for char in reversed(col_str):
        col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
        expn += 1
    return col_num