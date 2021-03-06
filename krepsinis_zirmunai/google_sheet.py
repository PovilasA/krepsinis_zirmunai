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
         self.new_matrix = worksheet_self.worksheet.range(string_range, 'cells')
         # new_matrix is the same as raw_matrix but later new_matrix will be 
         # changed and raw_matrix is NEVER changed

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

      class CellExtract:
         default = lambda x: x
         raw_value = lambda x: x.value
         color = lambda x: x.color
         text_format = lambda x: x.text_format
         wrap_strategy = lambda x: x.wrap_strategy
         borders = lambda x: x.borders
         formula = lambda x: x.formula
         horizontal_alignment = lambda x: x.horizontal_alignment
         note = lambda x: x.note if x.note is not None else ''
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

      def get_notes_matrix(self, headers=True, indices=False):
         return(self.extract(method='note', 
                             extract_format='matrix',
                             headers=headers,
                             indices=indices))

      def get_notes_dataframe(self, headers=True, indices=False):
         return(self.extract(method='note', 
                             extract_format='dataframe',
                             headers=headers,
                             indices=indices))

      def get_wrap_strategies_matrix(self, headers=True, indices=False):
         return(self.extract(method='wrap_strategy', 
                             extract_format='matrix',
                             headers=headers,
                             indices=indices))

      def get_wrap_strategies_datafrane(self, headers=True, indices=False):
         return(self.extract(method='wrap_strategy', 
                             extract_format='dataframe',
                             headers=headers,
                             indices=indices))


      def change(self, method, headers, indices, table):
         method = getattr(self.CellAssign, method)
         parsed_matrix = self.ParseTable(table, headers, indices, self.raw_matrix).output_table()
         # check dimensions of raw_matrix and table!
         # check table format!
         self.new_matrix = [[method(x_ij, v_ij) for x_ij,v_ij in zip(x_i,v_i)] 
                           for x_i,v_i in zip(self.new_matrix, parsed_matrix)]
         return(self)
         # TODO cells might be updated one-by-one (not all at once). For that
         # good idea would to track which cells were changed and then really 
         # update only changed cells. However, for this case this is not very
         # important that's why I skipped that. At least for a while.

      class CellAssign:
         def default(cell, new_cell): cell = new_cell; return(cell)
         def raw_value(cell, new_value): cell.value = new_value; return(cell)
         def color(cell, new_color): cell.color = new_color; return(cell)
         def text_format(cell, new_text_format): cell.text_format = new_text_format; return(cell)
            
         def wrap_strategy(cell, new_wrap_strategy): 
            # Example: new_wrap_strategy in ['WRAP_STRATEGY_UNSPECIFIED','OVERFLOW_CELL','LEGACY_WRAP','CLIP','WRAP']
            cell.wrap_strategy = new_wrap_strategy; return(cell)

         def borders(cell, new_borders): 
            # borders example:
            # {'bottom': {'color': {}, 'style': 'SOLID', 'width': 1},
            #  'left': {'color': {}, 'style': 'SOLID', 'width': 1},
            #  'right': {'color': {}, 'style': 'SOLID', 'width': 0},
            #  'top': {'color': {}, 'style': 'SOLID', 'width': 1}}
            cell.borders = new_borders; update(cell); return(cell)

         def formula(cell, new_formula): cell.formula = new_formula; return(cell)

         def horizontal_alignment(cell, new_hor_align):
            # Example: new_hor_align in '[CENTER','RIGHT','LEFT']
            cell.horizontal_alignment = gc.pygsheets.custom_types.HorizontalAlignment(new_hor_align)
            return(cell)

         def note(cell, new_note): cell.note = new_note; return(cell)

      class ParseTable:
         def __init__(self, table, headers, indices, raw_matrix):
            self.table = table
            self.headers = headers
            self.indices = indices
            self.raw_matrix = raw_matrix
            self.table_is_dataframe = None
            self.table_is_matrix = None
            self.parsed_table = None
            self.table_format = self.validate_table()

         def validate_table(self):
            if not self.is_dataframe() and not self.is_matrix():
               m = 'Given table format is not acceptable! It is not a matrix (list of lists) or dataframe!'
               raise Worksheet._Range.ParseTableError(m)
            expected_dim = [len(self.raw_matrix),len(self.raw_matrix[0])]
            actual_dim = self.table_dimensions()
            if expected_dim != actual_dim:
               m = 'Given table dimensions (%s) are not the same as raw_matrix dimensions (which is %s)!' % (actual_dim, expected_dim)
               raise Worksheet._Range.ParseTableError(m)
            return('dataframe' if self.is_dataframe() else 'matrix')
         
         def is_dataframe(self):
            if self.table_is_dataframe is None:
               self.table_is_dataframe = isinstance(self.table, pd.DataFrame)
            return(self.table_is_dataframe)

         def is_matrix(self):
            if self.table_is_matrix is None:
               self.table_is_matrix = False
               if isinstance(self.table, list):
                  if all(isinstance(x, list) for x in self.table):
                     lengths = [len(x) for x in self.table]
                     if len(list(set(lengths))) == 1:
                        self.table_is_matrix = True         
            return(self.table_is_matrix)

         def table_dimensions(self):
            if self.is_dataframe():
               dim = list(self.table.shape)
               if not self.headers:
                  dim[0] = dim[0] + 1
               if not self.indices:
                  dim[1] = dim[1] + 1
            if self.is_matrix():
               # Here we already know that table is "matrix" - list of lists with same sizes
               dim = [len(self.table),len(self.table[0])]
               if self.headers:
                  dim[0] = dim[0] - 1
               if self.indices:
                  dim[1] = dim[1] - 1
            return(dim)

         def output_table(self):
            parsed_table = self.table
            if self.is_dataframe():
               if not self.indices:
                  parsed_table = parsed_table.reset_index()
                  parsed_table.columns = [''] + list(parsed_table.columns[1::])
               if not self.headers:
                  parsed_table.loc[-1] = list(parsed_table.columns)  # adding a row
                  parsed_table.index = parsed_table.index + 1  # shifting index
                  parsed_table = parsed_table.sort_index()  # sorting by index
               parsed_table = parsed_table.values.tolist()
            if self.is_matrix():
               if self.headers:
                  parsed_table = parsed_table[1:]
               if self.indices:
                  parsed_table = [x_i[1:] for x_i in parsed_table]
            self.parsed_table = parsed_table
            return(parsed_table)

      class ParseTableError(Exception):
         pass

      def change_cells(self, table, headers=True, indices=True):
         return(self.change('default', headers, indices, table))

      def change_values(self, table, headers=True, indices=True):
         return(self.change('raw_value', headers, indices, table))

      def change_colors(self, table, headers=True, indices=True):
         return(self.change('color', headers, indices, table))

      def change_notes(self, table, headers=True, indices=True):
         return(self.change('note', headers, indices, table))

      def change_wrap_strategies(self, table, headers=True, indices=True):
         return(self.change('wrap_strategy', headers, indices, table))

      def set_changes(self):
         pass
         
         # TODO set_changes does not do anything at the moment. All changing 
         # part is being done in change() part instantly. There is a plan to fix 
         # this and apply changes only with set_changes(). Possible solution for
         # that could be to replace self.new_matrix with new class NewMatrix or 
         # new class NewCell. This class would have common methods like .value; 
         # .color and others (the same as pygsheets cell object). NewMatrix 
         # would be changed using change() and later those changes would be 
         # applied to worksheet using set_changes(). After this will be done 
         # test_set_changes() should also be updated with offline functionality.
         
         # TODO as mentioned in method change() this function might be updated
         # to change cells one-by-one and use mapping which cells to change 
         # created by change() method


class GoogleSpreadsheetNotFound(Exception):
   pass

class GoogleWorksheetNotFound(Exception):
   pass
