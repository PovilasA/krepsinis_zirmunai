import pandas as pd

class IndividualSummary:
   def __init__(self, parsed_input):
      self.parsed_input = parsed_input

   def Values(self):
      return IndividualSummary._Values(self.parsed_input)

   class _Values:
      def __init__(self, parsed_input):
         self.parsed_input = parsed_input
         
      def compute(self):
         result = pd.DataFrame()
         result['Sužaista'] = []
         result['Laimėta-Pralaimėta'] = []
         result['Taškų santykis'] = []
         result['Paskutiniai 5 kartai'] = []
         result['Paskutiniai 5 kartai (be praleidimų)'] = []
         result['Taškų santykis per paskutinius 5 kartus'] = []
         result['Serija'] = []
         result['Serija (be praleidimų)'] = []
         return(result)