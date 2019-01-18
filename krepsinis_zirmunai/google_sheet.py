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

      def extract(self, method, return_format, headers):
         method = getattr(self.Extractions, method)
         matrix = [[method(x_ij) for x_ij in x_i] for x_i in self.raw_matrix]
         table = self.Table(matrix, headers)
         if return_format == 'matrix':
            return(table.as_matrix())
         elif return_format == 'dataframe':
            return(table.as_dataframe())

      class Table:
         def __init__(self, matrix, headers):
            self.matrix = matrix
            self.headers = headers
         
         def as_matrix(self):
            if self.headers:
               pass
            else:
               return(self.matrix)
         
         def as_dataframe(self):
            pass

      class Extractions:
         default = lambda x: x
         raw_value = lambda x: x.value
         color = lambda x: x.color
         text_format = lambda x: x.text_format
         # More could be specified in the future. These functions are not tested!


      def cells_matrix(self, headers=True):
         return(self.extract(method='default', 
                             return_format='matrix',
                             headers=headers))

      def cells_dataframe(self, headers=True):
         return(
            extract(method='default', return_format='dataframe', headers=headers))
      
      def values_matrix(self, headers=True):
         return(
            extract(method='raw_values', return_format='matrix', headers=headers))

      def values_dataframe(self, headers=True):
         return(
            extract(method='raw_values', return_format='dataframe', headers=headers))

      def colors_matrix(self, headers=True):
         return(
            extract(method='color', return_format='matrix', headers=headers))

      def colors_dataframe(self, headers=True):
         return(
            extract(method='color', return_format='dataframe', headers=headers))

      
class GoogleSpreadsheetNotFound(Exception):
   pass

class GoogleWorksheetNotFound(Exception):
   pass
