from datetime import datetime
import re

import pytz

DATE_FORMATE1 = "%Y-%m-%d %H:%M:%S %Z%z"
DATE_FORMATE2= "%Y-%m-%d %H:%M:%S %Z"
DATE_FORMATE3= "%Y-%m-%d %H:%M:%S"




utc_zone = pytz.timezone('UTC')
_date = datetime.now(utc_zone).strftime(DATE_FORMATE1)
print(f'Date : {_date}')
print(f'Date  is valid : {re.match(TIME_REGEX3, _date)}')

utc_zone = pytz.timezone('UTC')
_date = datetime.now(utc_zone).strftime(DATE_FORMATE2)
print(f'Date : {_date}')
print(f'Date  is valid : {re.match(TIME_REGEX2, _date)}')

utc_zone = pytz.timezone('UTC')
_date = datetime.now(utc_zone).strftime(DATE_FORMATE3)
print(f'Date : {_date}')
print(f'Date  is valid : {re.match(TIME_REGEX1, _date)}')




