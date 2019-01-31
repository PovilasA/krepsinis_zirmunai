from krepsinis_zirmunai import google_client as gc
import pandas as pd

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
         self.new_matrix = None

      def extract(self, method, extract_format, headers, indices):
         method = getattr(self.CellExtract, method)
         matrix = [[method(x_ij) for x_ij in x_i] for x_i in self.raw_matrix]
         table = self.PrepareTable(matrix, headers, indices)
         if extract_format == 'matrix':
            return(table.as_matrix())
         elif extract_format == 'dataframe':
            return(table.as_dataframe())

      class PrepareTable:
         def __init__(self, matrix, headers, indices):
            self.matrix = matrix
            self.headers = headers
            self.indices = indices
         
         def as_matrix(self):
            mat = self.matrix
            if self.headers:
               mat = mat[1:]
            if self.indices:
               mat = [x_i[1:] for x_i in mat]
            return(mat)
         
         def as_dataframe(self):
            if self.indices and self.headers:
               headers = self.matrix.pop(0)
               if not headers[0].__hash__: # other option: isinstance(headers[0], collections.Hashable)
                  m = 'Object %s is not hashable and cannot be viewed as dataframe index!' % headers[0]
                  raise Worksheet._Range.PrepareTableError(m)
               df = pd.DataFrame(self.matrix, columns=headers).set_index(headers[0])

            if self.indices and not self.headers:
               df = pd.DataFrame(self.matrix).set_index(0)
               df.index = list(df.index.get_values())

            if not self.indices and self.headers:
               headers = self.matrix.pop(0)
               df = pd.DataFrame(self.matrix, columns=headers)

            if not self.indices and not self.headers:
               df = pd.DataFrame(self.matrix)
            return(df)

      class PrepareTableError(Exception):
         pass     
            pass
         pass     
            pass
         pass     
            pass
         pass     

      class CellExtract:
         default = lambda x: x
         raw_value = lambda x: x.value
         color = lambda x: x.color
         text_format = lambda x: x.text_format
         # More could be specified in the future. These functions are not tested!


      def get_cells_matrix(self, headers=True, indices=False):
         return(self.extract(method='default', 
                             extract_format='matrix',
                             headers=headers,
                             indices=indices))

      def get_cells_dataframe(self, headers=True, indices=False):
         return(self.extract(method='default', 
                             extract_format='dataframe',
                             headers=headers,
                             indices=indices))
      
      def get_values_matrix(self, headers=True, indices=False):
         return(self.extract(method='raw_value', 
                             extract_format='matrix',
                             headers=headers,
                             indices=indices))

      def get_values_dataframe(self, headers=True, indices=False):
         return(self.extract(method='raw_value', 
                             extract_format='dataframe',
                             headers=headers,
                             indices=indices))

      def get_colors_matrix(self, headers=True, indices=False):
         return(self.extract(method='color', 
                             extract_format='matrix',
                             headers=headers,
                             indices=indices))

      def get_colors_dataframe(self, headers=True, indices=False):
         return(self.extract(method='color', 
                             extract_format='dataframe',
                             headers=headers,
                             indices=indices))



      def change(self, method, assign_format, headers, indices, table):
         method = getattr(self.CellAssign, method)
         values = self.ParseTable(table, headers, indices)
         # check dimensions of raw_matrix and table!
         # check table format!
         self.new_matrix = [[method(x_ij, v_ij) for x_ij,v_ij in zip(x_i,v_i)] 
                           for x_i,v_i in zip(self.raw_matrix, values)]
         return(self)
         # TODO cells might be updated one-by-one (not all at once). For that
         # good idea would to track which cells were changed and then really 
         # update only changed cells. However, for this case this is not very
         # important that's why I skipped that. At least for a while.

      class CellAssign:
         def raw_value(cell, value): cell.value = value; return(cell)

      class ParseTable:
         # probably assign_format is not needed!
         def __init__(self, table, headers, indices):
            self.table = table
            self.headers = headers
            self.indices = indices
            self.validate_table()

         def validate_table(self):
            pass
            # Throw ParseTableError

      class ParseTableError(Exception):
         pass

      def set(self):
         self.pygsheets_worksheet.update_cells(self.string_range, self.new_matrix)
         # TODO as mentioned in method change() this function might be updated
         # to change cells one-by-one and use mapping which cells to change 
         # created by change() method


class GoogleSpreadsheetNotFound(Exception):
   pass

class GoogleWorksheetNotFound(Exception):
   pass
