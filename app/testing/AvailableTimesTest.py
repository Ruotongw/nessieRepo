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
    deadLine = '2018-11-02T00:00:00-05:00'
    nowDay = 29
    nowHour = 17
    nowMinute = 30
    workStart = 6
    workEnd = 23
    event1 = {'start': {'dateTime': '2018-10-31T14:00:00-05:00', 'timeZone': 'America/Chicago'},
    'end': {'dateTime': '2018-10-31T15:00:00-05:00', 'timeZone': 'America/Chicago'}}


    # event2 = {'start': {'dateTime': '2019-01-01T14:00:00-05:00', 'timeZone': 'America/Chicago'},
    # 'end': {'dateTime': '2019-01-01T15:00:00-05:00', 'timeZone': 'America/Chicago'}}


    # event3 = {'start': {'dateTime': '2018-11-08T13:20:00-05:00', 'timeZone': 'America/Chicago'},
    # 'end': {'dateTime': '2018-11-08T16:30:00-05:00', 'timeZone': 'America/Chicago'}}
    #
    # event4 = {'start': {'dateTime': '2018-11-11T13:30:00-05:00', 'timeZone': 'America/Chicago'},
    # 'end': {'dateTime': '2018-11-11T15:30:00-05:00', 'timeZone': 'America/Chicago'}}
    #
    # event5 = {'start': {'dateTime': '2018-11-11T22:00:00-05:00', 'timeZone': 'America/Chicago'},
    # 'end': {'dateTime': '2018-11-11T23:30:00-05:00', 'timeZone': 'America/Chicago'}}

    events = [event1]

    findAvailableTimes(duration, deadLine, nowDay, nowHour, nowMinute, workStart, workEnd, events)

def findAvailableTimes(duration, deadLine, nowDay, nowHour, nowMinute, workStart, workEnd, events):

    estTimeMin = duration * 60
    estMins = estTimeMin % 60
    estHours = (estTimeMin - estMins) / 60

    availableTimes = []

    # openHours = range(openStartTime, openEndTime)
    # openMinutes = range(openStartTime * 60, openEndTime * 60)
    openHours, openMinutes = openTimeWindow(workStart,workEnd)

    for i in range(len(events) - 1):
        event1 = events[i]
        event2 = events[i + 1]

        e1, e2 = formatEvent(event1, event2)

        sameDay = (e1.day == e2.day)

        #for time in morning before eventTime
        morningTime = (e2.hour * 60 + e2.minute) - (workStart*60)
        enoughMorningTime = morningTime >= estTimeMin + 30

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

        print(timeWindow not in openMinutes)

        if(currentTime and (sameDay and enoughTime and (e1.hour in openHours) and (timeWindow in openMinutes))):
            timeSlot = generalTimeSlot(e1, duration)
            availableTimes.append(timeSlot)

        if(currentTime and (not sameDay and enoughTime2 and (e1.hour in openHours) and (timeWindow in openMinutes))):
            timeSlot = generalTimeSlot(e1, duration)
            availableTimes.append(timeSlot)

        if(not sameDay and enoughMorningTime):
            timeSlot = morningTimeSlot(e2, duration)
            availableTimes.append(timeSlot)

    lastEvent = events[len(events) - 1]
    lastEnd, lastStart = formatEvent(lastEvent, lastEvent)

    timeWindow = (lastEnd.hour * 60) + lastEnd.minute + (estTimeMin + 30)

    beforeTime = (lastStart.hour * 60 + lastStart.minute) - (workStart*60)
    enoughBeforeTime = beforeTime >= estTimeMin + 30

    timeDiff = (lastStart.hour * 60 + lastStart.minute) - (nowHour * 60 + nowMinute)
    enoughTime = timeDiff >= (estTimeMin + 30)

    diffDays = lastStart.day != nowDay

    if(enoughBeforeTime and (enoughTime or diffDays)):
        timeSlot = morningTimeSlot(lastStart, duration)
        availableTimes.append(timeSlot)

    if((lastEnd.hour in openHours) and (timeWindow in openMinutes)):
        timeSlot = generalTimeSlot(lastEnd, duration)
        availableTimes.append(timeSlot)

    print(availableTimes)
    return availableTimes

def morningTimeSlot(event2, duration):
    event2Min = (event2.hour * 60) + event2.minute
    duration = duration * 60

    startTime = event2Min - duration - 15
    startMin = startTime % 60
    startHour = (startTime - startMin) / 60

    endTime = event2Min -15
    endMin = endTime % 60
    endHour = (endTime - endMin)/60

    eventStart = formatDT2(event2.year, event2.month, event2.day, startHour, startMin, event2.second)
    eventEnd = formatDT2(event2.year, event2.month, event2.day, endHour, endMin, event2.second)

    timeSlot = [eventStart, eventEnd]
    return timeSlot

def generalTimeSlot(event1, duration):
    event1Min = (event1.hour * 60) + event1.minute
    duration = duration * 60

    startTime = event1Min + 15
    startMin = startTime % 60
    startHour = (startTime - startMin) / 60

    endTime = startTime + duration
    endMin = endTime % 60
    endHour = (endTime - endMin)/60

    eventStart = formatDT2(event1.year, event1.month, event1.day, startHour, startMin, event1.second)
    eventEnd = formatDT2(event1.year, event1.month, event1.day, endHour, endMin, event1.second)

    timeSlot = [eventStart, eventEnd]
    return timeSlot

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
