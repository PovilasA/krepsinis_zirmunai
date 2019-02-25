from krepsinis_zirmunai import google_client as gc
from krepsinis_zirmunai import google_sheet as gs
from krepsinis_zirmunai.statistics.read_input_data import *

from mock import call, MagicMock
import pytest
from pytest_mock import mocker 

import csv
from freezegun import freeze_time

from tests.run_online_tests import *

client = gc.Pygsheets().authenticate().get_client()
test_spreadsheet_name ='krepsinis_zirmunai_test_spreadsheet'

def create_test_spreadsheet(named_index=False):
   spreadsheet = client.create(test_spreadsheet_name)
   worksheet = spreadsheet.worksheet_by_title('Sheet1')
   return(spreadsheet, worksheet)

def delete_test_spreadsheet():
   client.open(test_spreadsheet_name).delete()
