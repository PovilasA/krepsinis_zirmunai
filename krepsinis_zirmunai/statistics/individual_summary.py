import pandas as pd
import numpy as np

class IndividualSummary:
   def __init__(self, parsed_input):
      self.parsed_input = parsed_input
      self.rows = parsed_input.index
      self.columns = ['Sužaista','Laimėta-Pralaimėta','Taškų santykis',
                      'Paskutiniai 5 kartai','Paskutiniai 5 kartai (be praleidimų)',
                      'Taškų santykis per paskutinius 5 kartus','Serija',
                      'Serija (be praleidimų)']

   def Notes(self):
      return IndividualSummary._Notes(self)

   class _Notes:
      def __init__(self, ind_sum_self):
         self.columns = ind_sum_self.columns
         self.rows = ind_sum_self.rows
         
      def compute(self):
         text1 = "W - laimėta\n"
         text2 = "L - pralaimėta\n"
         text3 = "D - baigta lygiosiomis arba rezultatas neužfiksuotas\n"
         text4 = "'-' - žaidėjo nebuvo"
         notes_dict = {
            '': '',
            'Sužaista': '',
            'Laimėta-Pralaimėta': '',
            'Taškų santykis': '',
            'Paskutiniai 5 kartai': text1+text2+text3,
            'Paskutiniai 5 kartai (be praleidimų)':text1+text2+text3+text4,
            'Taškų santykis per paskutinius 5 kartus': '',
            'Serija': '',
            'Serija (be praleidimų)': ''
         }
         notes = [['']*(len(self.columns)+1)]*(len(self.rows)+1)
         notes[0] = list(notes_dict.keys())
         notes[0] = [notes_dict[n] for n in notes[0]]
         return notes

   def WrapStrategies(self):
      return IndividualSummary._WrapStrategies(self)

   class _WrapStrategies:
      def __init__(self, ind_sum_self):
         self.columns = ind_sum_self.columns
         self.rows = ind_sum_self.rows
         
      def compute(self):
         wrap_strategies = [['WRAP_STRATEGY_UNSPECIFIED']*(len(self.columns)+1)]*(len(self.rows)+1)
         wrap_strategies[0] = ['WRAP' for w in wrap_strategies[0]]
         return wrap_strategies

   def ColumnWidths(self):
      w = [100]*(len(self.columns)+1)
      w[0] = 150
      return w

   def Values(self):
      return IndividualSummary._Values(self)

   class _Values:
      def __init__(self, ind_sum_self):
         self.parsed_input = ind_sum_self.parsed_input
         self.columns = ind_sum_self.columns
         self.rows = ind_sum_self.rows
         
      def compute(self):
         result = pd.DataFrame(index = self.rows, columns = self.columns)
         result['Sužaista'] = self.games_played()
         result['Laimėta-Pralaimėta'] = self.won_and_lost()
         result['Taškų santykis'] = self.point_difference()
         result['Paskutiniai 5 kartai'] = self.last_5_record()
         result['Paskutiniai 5 kartai (be praleidimų)'] = self.last_5_record_wo_absence()
         result['Taškų santykis per paskutinius 5 kartus'] = self.point_difference_last_5()
         result['Serija'] = self.streak()
         result['Serija (be praleidimų)'] = self.streak_wo_absence()
         result = self.sort(result)
         return(result)

      def sort(self, result):
         result['temp'] = result['Sužaista'].astype('int')
         return result.sort_values('temp', ascending=False).drop('temp', axis=1)


      # Column 'Sužaista'
      def games_played(self):
         return(np.isfinite(self.parsed_input).sum(axis=1).astype('str'))

      # Column 'Laimėta-Pralaimėta'
      def won_and_lost(self):
         won = (self.parsed_input > 0).sum(axis=1)
         lost = (self.parsed_input < 0).sum(axis=1)
         return([str(w) + ' - ' + str(l) for (w,l) in zip(won,lost)])

      # Column 'Taškų santykis'
      def point_difference(self):
         p = self.parsed_input.sum(axis=1)
         return(point_difference_to_plus_minus(p))

      # Column 'Paskutiniai 5 kartai'
      def last_5_record(self):
         last_cols = self.parsed_input[self.parsed_input.columns[-5:]]
         r = [''.join(reversed([result_to_letter(i) for i in row])) for _,row in last_cols.iterrows()]
         return(r)
      
      # Column 'Paskutiniai 5 kartai (be praleidimų)'
      def last_5_record_wo_absence(self):
         df = self.parsed_input
         r = [''.join([result_to_letter(i) for i in reversed(row.dropna()[-5:])]) for _,row in df.iterrows()]
         return(r)

      # Column 'Taškų santykis per paskutinius 5 kartus'
      def point_difference_last_5(self):
         p = [sum(row.dropna()[-5:]) for _,row in self.parsed_input.iterrows()]
         return(point_difference_to_plus_minus(p))

      # Column 'Serija'
      def streak(self):
         return([self.__individual_streak(row) for _,row in self.parsed_input.iterrows()])

      # Column 'Serija (be praleidimų)'
      def streak_wo_absence(self):
         return([self.__individual_streak(row.dropna()) for _,row in self.parsed_input.iterrows()])

      def __individual_streak(self, list):
         streaks_count = IndividualSummary._Values.Streaks(list).get()
         longest_streak_types = [k for k,v in streaks_count.items() if v == max(streaks_count.values())]
         
         priority = {'win':6,'lose':5,'draw':4,'not_lost':3,'not_win':2,'absence':1}
         state_dict = {'win':"Laimėjo",
                       'lose':"Pralaimėjo",
                       'draw':'Lygiosios',
                       'not_lost':'Nepralaimėjo',
                       'not_win':'Nelaimėjo',
                       'absence':'Nebuvo'}
         
         longest_streaks_dict = {k:v for k,v in priority.items() if k in longest_streak_types}
         one_longest_streak = [k for k,v in longest_streaks_dict.items() if v == max(longest_streaks_dict.values())]
         result = state_dict[one_longest_streak[0]] + ' ' + str(streaks_count[one_longest_streak[0]])
         return(result)
      
      class Streaks:
         def __init__(self, list):
            self.list = list[::-1]

         def get(self):
            return({
               'win': self.__win_streak(),
               'lose': self.__lose_streak(),
               'not_lost': self.__not_lose_streak(),
               'not_win': self.__not_win_streak(),
               'draw': self.__draw_streak(),
               'absence': self.__absence_streak()
            })

         def find_streak_length(self, condition_method):
            try:
               last_ind = next(i for i, v in enumerate(self.list) if not condition_method(v))
            except StopIteration:
               last_ind = len(self.list)
            return(last_ind)

         def __win_streak(self):
            f = lambda x: x > 0
            return(self.find_streak_length(f))

         def __lose_streak(self):
            f = lambda x: x < 0
            return(self.find_streak_length(f))

         def __not_lose_streak(self):
            f = lambda x: x >= 0
            return(self.find_streak_length(f))

         def __not_win_streak(self):
            f = lambda x: x <= 0
            return(self.find_streak_length(f))

         def __draw_streak(self):
            f = lambda x: x == 0
            return(self.find_streak_length(f))

         def __absence_streak(self):
            f = lambda x: np.isnan(x)
            return(self.find_streak_length(f))


         
def result_to_letter(r):
   return 'W' if r > 0 else 'L' if r < 0 else 'D' if r == 0  else '-'

def point_difference_to_plus_minus(list):
   positive = lambda i: '="+' + str(int(i)) + '"'
   negative = lambda i: '="' + str(int(i)) + '"'
   return [positive(i) if i > 0 else negative(i) for i in list]