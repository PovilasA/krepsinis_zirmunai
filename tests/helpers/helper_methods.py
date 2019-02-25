from krepsinis_zirmunai import google_client as gc
from krepsinis_zirmunai import google_sheet as gs

test_spreadsheet_name ='krepsinis_zirmunai_test_spreadsheet'

def create_test_spreadsheet(client, insert_values = True, named_index=False):
   spreadsheet = client.create(test_spreadsheet_name)
   worksheet = spreadsheet.worksheet_by_title('Sheet1')
   if insert_values:
      worksheet.cell('B1').value = 'value_B1'
      worksheet.cell('B2').value = 2
      worksheet.cell('A2').value = 1
      if named_index:
         worksheet.cell('A1').value = 'index_name'
         worksheet.cell('A1').color = (1, 1, 0, 0)
   return(spreadsheet, worksheet)

def delete_test_spreadsheet(client):
   client.open(test_spreadsheet_name).delete()

def create_range(client, string_range = 'A1:C2', named_index='False'):
   _,_ = create_test_spreadsheet(client, named_index=named_index)
   wks = gs.Worksheet(client, test_spreadsheet_name, 'Sheet1')
   wks_range = wks.Range(string_range)
   return(wks_range)
