from krepsinis_zirmunai import google_sheet as gs

class ReadInputData:
   def __init__(self, client, spreadsheet_name, worksheet_name, top_values = 12):
      self.worksheet = gs.Worksheet(client, spreadsheet_name, worksheet_name)
      matrix = self.worksheet.worksheet.get_all_values()
      self.string_range = find_string_range(matrix)
      self.values_matrix = self.worksheet.Range(self.string_range).get_values_matrix(False, False)
      self.colors_matrix = self.worksheet.Range(self.string_range).get_colors_matrix(False, False)
      self.top_values = top_values
      
   # We make assumption that first column in matrix is names of players
   # first row is results and second row - time of game played

# General methods that might be used in other classes also

def find_string_range(matrix):
   min_row = min_col = max(len(matrix),len(matrix[0]))
   max_row = max_col = 0
   for i in range(len(matrix)):
      for j in range(len(matrix[i])):
         if matrix[i][j] != '':
            max_row = max(max_row, i); max_col = max(max_col, j)
            min_row = min(min_row, i); min_col = min(min_col, j)
   min_row = min_row + 1; min_col = min_col + 1
   max_row = max_row + 1; max_col = max_col + 1
   return(num_to_col_letters(min_col) + str(min_row) + ':' + 
          num_to_col_letters(max_col) + str(max_row))

def num_to_col_letters(num):
   letters = ''
   while num:
      mod = (num - 1) % 26
      letters += chr(mod + 65)
      num = (num - 1) // 26
   return ''.join(reversed(letters))
