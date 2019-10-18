from krepsinis_zirmunai import google_client as gc
from krepsinis_zirmunai import google_sheet as gs

from krepsinis_zirmunai.statistics.read_input_data import *
from krepsinis_zirmunai.statistics.individual_summary import *
from krepsinis_zirmunai.statistics.write_results import *


# Parameters
# SPREADSHEET_NAME = 'krepsinis zirmunai copy'
# INPUT_WORKSHEET_NAME = 'Lankomumas'
# OUTPUT_WORKSHEET_NAME = 'Statistika1'

SPREADSHEET_NAME = 'Krepšinis Žirmūnai 20:00 - 21:30'
INPUT_WORKSHEET_NAME = 'Lankomumas 2019-2020'
OUTPUT_WORKSHEET_NAME = 'Statistika 2019-2020'
TOP_VALUES = 14          # how many players    
IND_SUM_RANGE = 'B3:J17' # where it is saved 

def calculate():
   import time; start = time. time()

   client = gc.Pygsheets().authenticate().get_client()
   parsed_input = ReadInputData(client, SPREADSHEET_NAME, 
                                INPUT_WORKSHEET_NAME, TOP_VALUES).parse()
   
   individual_summary = IndividualSummary(parsed_input)
   WriteResults(client, SPREADSHEET_NAME, OUTPUT_WORKSHEET_NAME,
                individual_summary, IND_SUM_RANGE).execute()

   end = time.time()
   output = "Statistics were succesfully calculated using spreadsheet's '%s' "\
            "worksheet '%s' and saved into worksheet '%s'. Calculation time "\
            "was about %s seconds." %(SPREADSHEET_NAME, 
                                      INPUT_WORKSHEET_NAME, 
                                      OUTPUT_WORKSHEET_NAME, 
                                      round(end-start))
   print(output)

if __name__ == '__main__':
   calculate()