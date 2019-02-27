import pandas as pd
import numpy as np

class IndividualSummary:
   def __init__(self, parsed_input):
      self.parsed_input = parsed_input

   def Values(self):
      return IndividualSummary._Values(self.parsed_input)

   class _Values:
      def __init__(self, parsed_input):
         self.parsed_input = parsed_input
         
      def compute(self):
         result = pd.DataFrame(index = self.parsed_input.index)
         result['Sužaista'] = self.games_played()
         result['Laimėta-Pralaimėta'] = self.won_and_lost()
         # from IPython import embed; embed()
         result['Taškų santykis'] = self.point_difference()
         result['Paskutiniai 5 kartai'] = self.last_5_record()
         result['Paskutiniai 5 kartai (be praleidimų)'] = self.last_5_record_wo_absence()
         result['Taškų santykis per paskutinius 5 kartus'] = self.point_difference_last_5()
         result['Serija'] = self.streak()
         # result['Serija (be praleidimų)'] = self.streak_wo_absence()
         return(result)

      # Column 'Sužaista'
      def games_played(self):
         return(np.isfinite(self.parsed_input).sum(axis=1))

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
         
         
def result_to_letter(r):
   return('W' if r > 0 else 'L' if r < 0 else 'D' if r == 0  else '-')

def point_difference_to_plus_minus(list):
   return(['+' + str(int(i)) if i > 0 else str(int(i)) for i in list])

