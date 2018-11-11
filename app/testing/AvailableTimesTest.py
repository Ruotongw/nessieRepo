from __future__ import print_function
import datetime
import random
import math
import pytz
from pytz import timezone
import time
# import tzlocal
# from tzlocal import get_localzone

def main():
    duration = 2
    deadLine = '2018-11-10T00:00:00-05:00'
    nowDay = 7
    nowHour = 17
    nowMinute = 30
    workStart = 6
    workEnd = 23
    event1 = {'start': {'dateTime': '2018-11-07T20:00:00-05:00', 'timeZone': 'America/Chicago'},
    'end': {'dateTime': '2018-11-07T22:00:00-05:00', 'timeZone': 'America/Chicago'}}


    event2 = {'start': {'dateTime': '2018-11-08T09:40:00-05:00', 'timeZone': 'America/Chicago'},
    'end': {'dateTime': '2018-11-08T10:40:00-05:00', 'timeZone': 'America/Chicago'}}


    event3 = {'start': {'dateTime': '2018-11-08T13:20:00-05:00', 'timeZone': 'America/Chicago'},
    'end': {'dateTime': '2018-11-08T16:30:00-05:00', 'timeZone': 'America/Chicago'}}

    event4 = {'start': {'dateTime': '2018-11-11T13:30:00-05:00', 'timeZone': 'America/Chicago'},
    'end': {'dateTime': '2018-11-11T15:30:00-05:00', 'timeZone': 'America/Chicago'}}

    event5 = {'start': {'dateTime': '2018-11-11T22:00:00-05:00', 'timeZone': 'America/Chicago'},
    'end': {'dateTime': '2018-11-11T23:30:00-05:00', 'timeZone': 'America/Chicago'}}

    events = [event1, event2, event3, event4, event5]

    findAvailableTimes(duration, deadLine, nowDay, nowHour, nowMinute, workStart, workEnd, events)

def findAvailableTimes(duration, deadLine, nowDay, nowHour, nowMinute, workStart, workEnd, events):

    estTimeMin = duration * 60
    estMins = estTimeMin % 60
    estHours = (estTimeMin - estMins) / 60

    availableTimes = []

    for i in range(len(events) - 1):
        event1 = events[i]
        event2 = events[i + 1]

        # print(event1['end'])
        # print(event2['start'])

        e1, e2 = formatEvent(event1, event2)

        # print(e1)
        # print(e2)

        sameDay = (e1.day == e2.day)

        # For events on the same day
        timeDiff = (e2.hour * 60 + e2.minute) - (e1.hour * 60 + e1.minute)
        enoughTime = timeDiff >= (estTimeMin + 30)

        # For events on different days
        timeDiff2 = (1440 - (e1.hour * 60) + e1.minute) + (e2.hour * 60 + e2.minute)
        enoughTime2 = timeDiff2 >= (estTimeMin + 30)

        # Ensures that the algorithm doesn't schedule events in the past
        currentTime = ((e1.hour == nowHour) and (e1.minute >= nowMinute)) or e1.hour > nowHour or (e1.day > nowDay)

        # Ensures that the entire scheduled event would be within the open working hours
        timeWindow = (e1.hour * 60) + e1.minute + (estTimeMin + 30)

        # openHours = range(openStartTime, openEndTime)
        # openMinutes = range(openStartTime * 60, openEndTime * 60)
        openHours, openMinutes = openTimeWindow(workStart,workEnd)

        if(currentTime and (sameDay and enoughTime and (e1.hour in openHours) and (timeWindow in openMinutes))
                or (not sameDay and enoughTime2 and (e1.hour in openHours) and (timeWindow in openMinutes))):

            startHour = e1.hour

            startMinute = e1.minute
            if startMinute + estMins >= 45:
                startHour += 1
                startMinute = 60 - startMinute
                startMinute = abs(startMinute - 15)
            else:
                startMinute += 15

            endHour = startHour + estHours
            endMinute = startMinute + estMins

            eventStart = formatDT2(e1.year, e1.month, e1.day, startHour, startMinute, e1.second)
            eventEnd = formatDT2(e1.year, e1.month, e1.day, endHour, endMinute, e1.second)

            timeSlot = [eventStart, eventEnd]
            availableTimes.append(timeSlot)
            print (len(availableTimes))

    print(availableTimes)
    return availableTimes

def openTimeWindow(openStartTime, openEndTime):
    openHours = range(openStartTime, openEndTime)
    openMinutes = range(openStartTime * 60, openEndTime * 60)
    return openHours, openMinutes

def formatEvent(event1, event2):
    fmt = '%Y-%m-%dT%H:%M:%S'

    e1str = event1['end'].get('dateTime')
    e2str = event2['start'].get('dateTime')

    e1str = e1str[:22] + e1str[23:]
    e2str = e2str[:22] + e2str[23:]

    e1 = datetime.datetime.strptime(e1str[:19], fmt)
    e2 = datetime.datetime.strptime(e2str[:19], fmt)

    utc = timezone('UTC')
    chi = timezone('America/Chicago')

    # e1 = e1.astimezone(utc)
    # e2 = e2.astimezone(utc)

    e1 = e1.replace(tzinfo=utc)
    e2 = e2.replace(tzinfo=utc)

    e1.strftime(fmt)
    e2.strftime(fmt)

    # e1, e2 = inDaylightSavings(e1, e2)

    e1.strftime(fmt) + '-05:00'
    e2.strftime(fmt) + '-05:00'

    # e1 = chi.normalize(e1)
    # e2 = chi.normalize(e2)

    print('-----------------------------------------')
    print(e1)
    print(e2)
    print('-----------------------------------------')

    return e1, e2

def inDaylightSavings(e1, e2):
    DSTMonths = [4, 5, 6, 7, 8, 9, 10]

    if (e1.month == 11 and e1.day < 4) or e1.month in DSTMonths:
        e1 = e1 + datetime.timedelta(hours = 0)
        e2 = e2 + datetime.timedelta(hours = 0)
    else:
        e1 = e1 + datetime.timedelta(hours = 1)
        e2 = e2 + datetime.timedelta(hours = 1)

    return e1, e2

def formatDT2(year, month, day, hour, minute, second):
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

main()
