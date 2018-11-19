#timeSlot.py
from __future__ import print_function
import datetime
import pytz
from pytz import timezone
import time
from tzlocal import get_localzone
from .format import *

# Handles time slot behavior.
class TimeSlot:
    def __init__(self, estimate):
        self.estimate = estimate
        global format
        format = Format()


    def beforeTimeSlot(self, event2):
        '''Returns the time slot before event2.'''

        localizedTime = self.estimate

        event2Min = (event2.hour * 60) + event2.minute
        localizedTime = localizedTime * 60

        startTime = event2Min - localizedTime - 15
        startMin = startTime % 60
        startHour = (startTime - startMin) / 60

        endTime = event2Min -15
        endMin = endTime % 60
        endHour = (endTime - endMin)/60

        eventStart = format.formatDT2(event2.year, event2.month, event2.day, startHour, startMin, event2.second)
        eventEnd = format.formatDT2(event2.year, event2.month, event2.day, endHour, endMin, event2.second)

        timeSlot = [eventStart, eventEnd]
        return timeSlot


    def afterTimeSlot(self, event1):
        '''Returns the time slot after event1.'''

        localizedTime = self.estimate

        event1Min = (event1.hour * 60) + event1.minute
        localizedTime = localizedTime * 60

        startTime = event1Min + 15
        startMin = startTime % 60
        startHour = (startTime - startMin) / 60

        endTime = startTime + localizedTime
        endMin = endTime % 60
        endHour = (endTime - endMin)/60

        eventStart = format.formatDT2(event1.year, event1.month, event1.day, startHour, startMin, event1.second)
        eventEnd = format.formatDT2(event1.year, event1.month, event1.day, endHour, endMin, event1.second)

        timeSlot = [eventStart, eventEnd]
        return timeSlot
