#format.py
from __future__ import print_function
import datetime
import pytz
from pytz import timezone
import time
from tzlocal import get_localzone

# Handles the formatting of dateTime objects.
class Format:
    def __init__(self):
        pass

    def formatEvent(self, event1, event2):
        '''Returns event1 and event2 in the correct datetime format to use in
        findAvailableTimes(). This requires turning the start and end time strings
        into dateTime objects, converting them to UTC time, and normalizing them to
        account for daylight savings time.'''

        fmt = '%Y-%m-%dT%H:%M:%S%z'

        e1str = event1['end'].get('dateTime')
        e2str = event2['start'].get('dateTime')

        e1str = e1str[:22] + e1str[23:]
        e2str = e2str[:22] + e2str[23:]

        e1 = datetime.datetime.strptime(e1str, fmt)
        e2 = datetime.datetime.strptime(e2str, fmt)

        utc = timezone('UTC')
        chi = timezone('America/Chicago')

        e1 = e1.astimezone(utc)
        e2 = e2.astimezone(utc)

        e1.strftime(fmt)
        e2.strftime(fmt)

        e1, e2 = self.inDaylightSavings(e1, e2)

        e1.strftime(fmt)
        e2.strftime(fmt)

        e1 = chi.normalize(e1)
        e2 = chi.normalize(e2)

        return e1, e2

    def formatDT1(self, dt):
        '''Returns a datetime string of the given datetime object formatted
        correctly for the Google API.'''

        fmt = '%Y-%m-%dT%H:%M:%S%z'
        dt = dt.strftime(fmt)
        dt = dt[:22] + ':' + e2[22:]

        return dt


    def formatDT2(self, year, month, day, hour, minute, second):
        '''Returns a datetime string with the given integers formatted correctly
        for the Google API.'''

        year = str(year)

        month = int(month)
        month = str(month)
        if int(month) < 10:
            month = '0' + month

        day = int(day)
        day = str(day)
        if int(day) < 10:
            day = '0' + day

        hour = int(hour)
        hour = str(hour)
        if int(hour) < 10:
            hour = '0' + hour

        minute = int(minute)
        minute = str(minute)
        if int(minute) < 10:
            minute = '0' + minute

        second = int(second)
        second = str(second)
        if int(second) < 10:
            second = '0' + second

        dt = (year + '-' + month + '-' + day +
                        'T' + hour + ':' + minute + ':' +
                        second + '-05:00')

        return dt

    def inDaylightSavings(self, e1, e2):
        '''Checks whether event1 and e2 are in daylight savings time and adds an
        hour accordingly.'''

        DSTMonths = [4, 5, 6, 7, 8, 9, 10]

        if (e1.month == 11 and e1.day < 4) or e1.month in DSTMonths:
            e1 = e1 + datetime.timedelta(hours = 0)
            e2 = e2 + datetime.timedelta(hours = 0)
        else:
            e1 = e1 + datetime.timedelta(hours = 1)
            e2 = e2 + datetime.timedelta(hours = 1)

        return e1, e2
