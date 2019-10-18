from krepsinis_zirmunai import google_sheet as gs
import pandas as pd
import datetime as dt
import numpy as np
import copy

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

   def parse(self):
      scores = self.__parse_scores()
      
      values = copy.deepcopy(self.values_matrix)
      colors = copy.deepcopy(self.colors_matrix)

      values, colors = self.__clean_matrices(values, colors)
      values = self.__iterate_values(values, colors, scores)

      return(values)

   # PRIVATE METHODS

   def __parse_scores(self):
      scores_list = [[i for i in sc.split('-')] for sc in self.values_matrix[0]]
      scores = [int(sc[0])-int(sc[1]) if len(sc) == 2 else 0 for sc in scores_list]
      scores = dict(zip(self.values_matrix[1], scores))
      return(scores)

   def __clean_matrices(self, values, colors):
      values = values[1:] # Remove first row which contains scores
      colors = colors[2:] # Remove first and second row which contains scores and dates
      colors = [c[1:] for c in colors] # Remove first column which contains player names

      # Extracting player names and game dates
      game_dates = values[0][1:] # headers
      player_names = [v[0] for v in values][1:] # rows

      # Removing first row and first column from values to have only raw values
      values = [v[1:] for v in values]
      values = values[1:]

      # Makes dataframes with the same columns and rows
      values = pd.DataFrame(values, columns=game_dates, index=player_names)
      colors = pd.DataFrame(colors, columns=game_dates, index=player_names)
      
      # Make all values numeric or Nan
      values = values.apply(pd.to_numeric, errors='coerce')

      # Removing rows without names and columns below current date
      time_now = dt.datetime.now().strftime("%Y-%m-%d")
      columns_to_keep = [h < time_now and h != '' for h in game_dates]
      values = values.loc[values.index != '', columns_to_keep]
      colors = colors.loc[colors.index != '', columns_to_keep]

      # Taking only top rows of data frame according to top_values variable
      values = values.head(self.top_values)
      colors = colors.head(self.top_values)

      return(values, colors)

   def __iterate_values(self, values, colors, scores):
      for game_date in values.columns:
         for player in values.index:
            cell_value = values.loc[player,game_date]
            cell_color = colors.loc[player,game_date]
            try:
               cell_value = float(cell_value)
               new_cell_value = scores[game_date]*self.__result_sign(cell_color) if cell_value > 0 else np.nan
            except ValueError:
               new_cell_value = np.nan
            values.loc[player,game_date] = new_cell_value
      return(values)

   def __result_sign(self, cell_color):
      c = cell_color
      return(1 if self.__first_team(c) else -1 if self.__second_team(c) else 0)

   def __first_team(self, color_code):
      return(color_code == (1, 1, 1, 0) or color_code == (None,None,None,None)) # white

   def __second_team(self, color_code):
      return(color_code == (0.2901961, 0.5254902, 0.9098039, 0)) # blue


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
