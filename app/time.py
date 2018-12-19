#currentTime.py
from __future__ import print_function
import datetime
import pytz
from pytz import timezone
import time
from tzlocal import get_localzone

#Handle retrieving and manipulating the current time.
class Time:
    def __init__(self):
        pass

    def getNowDHM(self, now):
        """Return the day, hour, and minute values for the current time.

        Keyword arguments:
        now -- a string representing the current date and time
        """
        now = now[:22] + now[23:]
        now = datetime.datetime.strptime(now, '%Y-%m-%dT%H:%M:%S%z')

        nowDay = now.day
        nowHour = now.hour
        nowMinute = now.minute
        return nowDay, nowHour, nowMinute


    def getNowYM(self, now):
        """Return the year and month values for the current time.

        Keyword arguments:
        now -- a string representing the current date and time
        """
        now = now[:22] + now[23:]
        now = datetime.datetime.strptime(now, '%Y-%m-%dT%H:%M:%S%z')

        nowYear = now.year
        nowMonth = now.month
        return nowYear, nowMonth


    def currentTime(self):
        """Return the current Chicago time in the correct string format to use with Google's API."""
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
        """Check whether the inputted datetime is in daylight savings. Return true if it is.

        Keyword arguments:
        dt -- a datetime object
        """
        #Source for checking daylight savings time:
        #https://stackoverflow.com/questions/5590429/calculating-daylight-saving-time-from-only-date
        lastSunday = dt.day - dt.weekday()
        if (dt.month < 3 or dt.month > 11):
            return False
        elif (dt.month > 3 or dt.month < 11):
            return True
        elif (dt.month == 3):
            return lastSunday >= 8
        else:
            return lastSunday <= 0
