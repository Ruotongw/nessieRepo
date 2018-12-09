#currentTime.py
from __future__ import print_function
import datetime
import pytz
from pytz import timezone
import time
from tzlocal import get_localzone

# Handles finding and manipulating the current time.
class Time:
    def __init__(self):
        pass

    def getNowDHM(self, now):
        '''Returns the day, hour, and minute value for the current time.'''

        now = now[:22] + now[23:]
        now = datetime.datetime.strptime(now, '%Y-%m-%dT%H:%M:%S%z')

        nowDay = now.day
        nowHour = now.hour
        nowMinute = now.minute
        return nowDay, nowHour, nowMinute


    def getNowYM(self, now):
        now = now[:22] + now[23:]
        now = datetime.datetime.strptime(now, '%Y-%m-%dT%H:%M:%S%z')

        nowYear = now.year
        nowMonth = now.month
        return nowYear, nowMonth


    def currentTime(self):
        '''Returns the current Chicago time, accounting for daylight savings and
        in the correct string format to use with Google's API.'''

        chi = timezone('America/Chicago')
        fmt = '%Y-%m-%dT%H:%M:%S%z'

        utcDt = datetime.datetime.utcnow()
        localDt = utcDt.replace(tzinfo=chi)
        localDt.strftime(fmt)

        # Offsets the time from UTC to Chicago
        offset = localDt - datetime.timedelta(hours = 5)
        offset.strftime(fmt)

        now = chi.normalize(offset)

        # Formats and adds necessary colon
        now = now.strftime(fmt)
        now = now[:22] + ':' + now[22:]

        return now


    def isDST(self, dt):
        '''CODE ATTRIBUTION:
        https://stackoverflow.com/questions/5590429/calculating-daylight-saving-time-from-only-date'''

        lastSunday = dt.day - dt.weekday()
        if (dt.month < 3 or dt.month > 11):
            return False
        elif (dt.month > 3 or dt.month < 11):
            return True
        elif (dt.month == 3):
            return lastSunday >= 8
        else:
            return lastSunday <= 0
