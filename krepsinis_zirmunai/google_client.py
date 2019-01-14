import os
import pygsheets
from IPython import embed

class Pygsheets:

   def __init__(self, credentials_file = 'credentials.json'):
      self.credentials_file = credentials_file
      self.authentication_completed = False

   def authenticate(self):
      message = 'Your specified credentials file does not exist!'
      if not self.__credentials_exists(): raise PygsheetsClientError(message)
      try:
         self.client = pygsheets.authorize(client_secret=self.credentials_file)
      except:
         message = 'Pygsheets was not able to authenticate your account!'
         raise PygsheetsClientError(message)
      self.authentication_completed = True
      return(self)

   def get_client(self):
      if self.authentication_completed:
         return(self.client)
      else:
         m = 'Pygsheets client is not authenticated. Please run authenticate() method to authenticate and continue'
         raise PygsheetsClientError(m)

   def __credentials_exists(self):
      auth_file_exists = os.path.isfile('sheets.googleapis.com-python')
      if auth_file_exists: return(True) 
      creds_file_exists = os.path.isfile(self.credentials_file)
      return(True if creds_file_exists else False)

class PygsheetsClientError(Exception):
    pass
