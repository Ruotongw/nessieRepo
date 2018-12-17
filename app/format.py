#format.py
from __future__ import print_function
import datetime
import pytz
from pytz import timezone
import time
from tzlocal import get_localzone
from .time import *

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

    def eventFormatDictionary(self, eventTime, title):
        "Formats event as a dictionary to show start and end times"

        eventStart = eventTime[0]
        eventEnd = eventTime[1]
        formattedEvent = {
            'summary': title,
            'start': {
                'dateTime': eventStart,
                'timeZone': 'America/Chicago',
            },
            'end': {
                'dateTime': eventEnd,
                'timeZone': 'America/Chicago'
            },
        }
        return formattedEvent


    def formatDT2(self, year, month, day, hour, minute, second):
        '''Returns a datetime string with the given integers formatted correctly
        for the Google API.'''

        dt = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        fmt = '%Y-%m-%dT%H:%M:%S'
        dtFmt = dt.strftime(fmt)
        dtFmt += '-05:00'

        return dtFmt

    def inDaylightSavings(self, e1, e2):
        '''Checks whether event1 and e2 are in daylight savings time and adds an
        hour accordingly.'''

        current = Time()
        if not current.isDST(e1):
            e1 = e1 + datetime.timedelta(hours = 1)
            e2 = e2 + datetime.timedelta(hours = 1)
        else:
            e1 = e1 + datetime.timedelta(hours = 0)
            e2 = e2 + datetime.timedelta(hours = 0)

        return e1, e2
