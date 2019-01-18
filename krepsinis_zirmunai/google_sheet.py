from krepsinis_zirmunai import google_client as gc

class Worksheet:

   def __init__(self, client, spreadsheet_name, worksheet_name):
      self.client = client

      try:
         self.spreadsheet = client.open(spreadsheet_name)
      except (gc.pygsheets.SpreadsheetNotFound):
         m = 'Could not find a spreadsheet with title %s.' % spreadsheet_name
         raise GoogleSpreadsheetNotFound(m)
      
      try:
         self.worksheet = self.spreadsheet.worksheet_by_title(worksheet_name)
      except (gc.pygsheets.WorksheetNotFound):
         m = 'Could not find a worksheet with title %s.' % worksheet_name
         raise GoogleWorksheetNotFound(m)

   def read_cell(self, cell):
      return(self.worksheet.cell(cell).value)

   def Range(self, string_range):
      return Worksheet._Range(self, string_range)

   class _Range:

      def __init__(self, worksheet_self, string_range):
         self.pygsheets_worksheet = worksheet_self.worksheet
         self.spreadsheet_name = worksheet_self.spreadsheet.title
         self.worksheet_name = worksheet_self.worksheet.title
         self.string_range = string_range
         self.raw_matrix = worksheet_self.worksheet.range(string_range, 'cells')

      
class GoogleSpreadsheetNotFound(Exception):
   pass

class GoogleWorksheetNotFound(Exception):
   pass
