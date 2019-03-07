## krepsinis_zirmunai

### Introduction

This script was created to calculated aggregated statistics for amateur basketball team. 'krepsinis' means basketball in Lithuanian while 'zirmunai' is the place where this team plays. The script takes information from Google Spreadsheet using Google Sheets API (and its' wrapper `python` package `pygsheets`) calculates some statistics and writes that back to the same spreadsheet.


### Installation

requirements:

get list of currently installed packages (better to do this on cloud9 or other virtual env):
pip freeze > requirements.txt

install packages from requirements.txt
pip install -r requirements.txt

run tests with debugging (embed())
pytest -s tests 
https://docs.pytest.org/en/latest/capture.html

maybe try continous testing:
https://semaphoreci.com/community/tutorials/testing-python-applications-with-pytest


py.test tests_directory/foo.py tests_directory/bar.py -k 'test_001 or test_some_other_test'
This will run test cases with name test_001 and test_some_other_test deselecting the rest of the test cases.


install:
```pip install --upgrade google-api-python-client oauth2client```

to get credentials.json:
https://developers.google.com/sheets/api/quickstart/python

https://pygsheets.readthedocs.io/en/stable/

Examples: https://github.com/nithinmurali/pygsheets

Useful links:
https://visualgit.readthedocs.io/en/latest/pages/naming_convention.html
https://pygsheets.readthedocs.io/en/stable/
https://docs.pytest.org/en/latest/assert.html
https://www.tutorialspoint.com/python/python_classes_objects.htm
https://semaphoreci.com/community/tutorials/testing-python-applications-with-pytest
https://github.com/nithinmurali/pygsheets


### Usage

Credentials are not saved in this repository. You can get it from this private link in Google Drive [part1](https://drive.google.com/file/d/1zkNIWhjg07Q11RsssssssW3LQ91KWkCC9Ycs-tw1Q/view?usp=sharing) (TODO: update this link!!!)

Useful examples for nested classes
https://chenyuzuoo.github.io/posts/31044/

There are online and offline tests. Choose which one you want to run in tests/run_online_tests.py. 
Sometimes online tests are not full because something general is tested in offline tests. For example: initialization of trivial class variable

For code debugging you can:
If you are not in google_client.py file use simple:
```from IPython import embed```
```embed()```
Otherwise:
```from krepsinis_zirmunai import google_client as gc```
```gc.embed()```


TODO:
- refactor google_sheet.py
   - _Range to separate file
   - maybe get, change, set to different files
- refactor test_+_google_sheet.py:
   - supporting functions to separate file
   - test for get, change, set to different files (maybe even more separate files)
- dokumentuoti, ka kas daro. Ypac Range klaseje

_Range:
   get() indices and headers parodo  (yra True) ar istraukto daikto reiksmes turetu nueiti i indeksus ir headerius. t.y ar jis turi headerius ir indeksus
   Matricos atveju - buti ismesti
   True - gaunu "mazesni"
   False - gaunu "didesni" (toki kaip paprasiau)

   change() indices and headers parodo (yra True) ar irasoma lentele turi headerius ir indeksus ir jie turetu buti ismesti pries irasyma
   True - irasau "mazesni"
   False - irasau "didesni" (visa kaip paduodu)


Collapse all methods in Visual studio code:
Fold All (Ctrl+K Ctrl+0)
Unfold All (Ctrl+K Ctrl+J)
Fold Level n (CTRL+K CTRL+[n])