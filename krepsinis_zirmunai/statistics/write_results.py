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
         range = self.worksheet.Range(self.individual_summary_string_range)
         range.change_values(values, headers=False, indices=False)
         range.change_notes(notes, headers=False, indices=False)
         range.change_wrap_strategies(wrap_strategies, headers=False, indices=False)
         range.set_changes()
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