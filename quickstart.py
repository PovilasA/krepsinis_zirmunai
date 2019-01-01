from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
SAMPLE_SPREADSHEET_ID = '1kpEsJK8sUizQ-Dx4Cn4cTYBiYuRDmDdmWHHy90M67_s'
SAMPLE_RANGE_NAME = 'Class Data!A2:E'


from IPython import embed



def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API
    sheet = service.spreadsheets()
    
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    #embed()

    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s, %s' % (row[0], row[4]))

import pygsheets

def main():
    client = pygsheets.authorize(client_secret='credentials.json')
    sh = client.open('api_test_spreadsheet')
    sh = client.open('KrepsinisZirmunaiTest')
    wks = sh.sheet1

    header = wks.cell('A1')
    # header.value = 'Names'
    # header.text_format['bold'] = True # make the header bold
    # header.update()

    # The same can be achieved in one line
    # wks.cell('B1').set_text_format('bold', True).value = 'heights'

    # wks.adjust_row_height(1,pixel_size=111)
    # header.wrap_strategy = 'WRAP'


    # Examples: https://github.com/nithinmurali/pygsheets

    embed()


if __name__ == '__main__':
    main()
