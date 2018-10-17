from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import random
import math

SCOPES = 'https://www.googleapis.com/auth/calendar'

store = file.Storage('token.json')
creds = store.get()
service = build('calendar', 'v3', http=creds.authorize(Http()))

dueDate = datetime.datetime(2018, 10, 20, 14)
estTime = 2
title = 'Test Assignment'
restrictStart = 23
restrictEnd = 9


def main():
    setUp()
    createEvent()


def setUp():
    global store
    global creds

    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)


def getCalendarEvents():
    global service
    global dueDate

    now = datetime.datetime.utcnow().isoformat() + 'Z'

    dueDateFormatted = formatDT1(dueDate)
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                    timeMax = dueDateFormatted, singleEvents=True,
                                    orderBy = 'startTime').execute()

    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

    return events


def findAvailableTimes():
    global estTime
    global restrictEnd
    global restrictStart

    availableTimes = []

    events = getCalendarEvents()

    for i in range(len(events) - 1):
        e1 = events[i]
        e2 = events[i + 1]

        e1DT = e1['end'].get('dateTime')
        e2DT = e2['start'].get('dateTime')

        e1Year = int(e1DT[0:4])
        e2Year = int(e2DT[0:4])

        e1Month = int(e1DT[5:7])
        e2Month = int(e2DT[5:7])

        e1Day = int(e1DT[8:10])
        e2Day = int(e2DT[8:10])

        e1Hour = int(e1DT[11:13])
        e2Hour = int(e2DT[11:13])

        e1Minute = int(e1DT[14:16])
        e2Minute = int(e2DT[14:16])

        e1Second = int(e1DT[17:19])
        e2Second = int(e2DT[17:19])

        if ((e1Day == e2Day and (e2Hour - e1Hour) >= estTime and ((e1Hour - restrictStart) >= estTime or
                (e1Hour - restrictEnd) >= estTime)) or
                ((e1Day != e2Day) and  (restrictStart - e1Hour) >= estTime)):

            eventStart = formatDT2(e1Year, e1Month, e1Day, e1Hour, e1Minute, e1Second)
            eventEnd = formatDT2(e1Year, e1Month, e1Day, e1Hour + estTime, e1Minute, e1Second)

            timeSlot = [eventStart, eventEnd]
            availableTimes.append(timeSlot)

        # elif ((e1Day != e2Day) and  (restrictStart - e1Hour) >= estTime):
        #     eventStart = formatDT2(e1Year, e1Month, e1Day, e1Hour, e1Minute, e1Second)
        #     eventEnd = formatDT2(e1Year, e1Month, e1Day, e1Hour + estTime, e1Minute, e1Second)

    return availableTimes


def getEventTime():
    availableTimes = findAvailableTimes()

    length = len(availableTimes)
    x = random.randrange(0, length)

    eventTime = availableTimes[x]
    return eventTime


def createEvent():
    global title

    eventTime = getEventTime()
    eventStart = eventTime[0]
    eventEnd = eventTime[1]

    event = {
        'summary': title,
        'start': {
            'dateTime': eventStart,
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': eventEnd,
            'timeZone': 'America/Los_Angeles'
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print ('Event created: %s' % (event.get('summary')))


def formatDT1(dt):
    year = dt.year.__str__()

    month = dt.month.__str__()
    if int(month) < 10:
        month = '0' + month

    day = dt.day.__str__()
    if int(day) < 10:
        day = '0' + day

    hour = dt.hour.__str__()
    if int(hour) < 10:
        hour = '0' + hour

    minute = dt.minute.__str__()
    if int(minute) < 10:
        minute = '0' + minute

    second = dt.second.__str__()
    if int(second) < 10:
        second = '0' + second

    formattedDt = (year + '-' + month + '-' + day +
                    'T' + hour + ':' + minute + ':' +
                    second + '-05:00')

    return formattedDt


def formatDT2(year, month, day, hour, minute, second):
    year = year.__str__()

    month = month.__str__()
    if int(month) < 10:
        month = '0' + month

    day = day.__str__()
    if int(day) < 10:
        day = '0' + day

    hour = hour.__str__()
    if int(hour) < 10:
        hour = '0' + hour

    minute = minute.__str__()
    if int(minute) < 10:
        minute = '0' + minute

    second = second.__str__()
    if int(second) < 10:
        second = '0' + second

    formattedDt = (year + '-' + month + '-' + day +
                    'T' + hour + ':' + minute + ':' +
                    second + '-05:00')

    return formattedDt

if __name__ == '__main__':
    main()
