from krepsinis_zirmunai import google_sheet as gs

class ReadInputData:
   def __init__(self, client, spreadsheet_name, worksheet_name, top_values = 12):
      self.worksheet = gs.Worksheet(client, spreadsheet_name, worksheet_name)
      matrix = self.worksheet.worksheet.get_all_values()
      self.string_range = find_string_range(matrix)
      self.values_matrix = self.worksheet.Range(self.string_range).get_values_matrix(False, False)
      self.colors_matrix = self.worksheet.Range(self.string_range).get_colors_matrix(False, False)
      self.top_values = top_values