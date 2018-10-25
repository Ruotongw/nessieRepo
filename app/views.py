# views.py
from __future__ import print_function
from flask import render_template, Flask, request, json
import os
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from app import app
import random
import math
import pytz


SCOPES = 'https://www.googleapis.com/auth/calendar'


store = file.Storage('app/static/token.json')
creds = store.get()
service = build('calendar', 'v3', http=creds.authorize(Http()))


@app.route('/', methods=['GET','POST'])
def main():

    store = file.Storage('app/static/token.json')
    creds = store.get()
    service = build('calendar', 'v3', http=creds.authorize(Http()))

    dueDate = datetime.datetime(2018, 10, 20, 14)
    estTime = 1
    restrictStart = 23
    restrictEnd = 9


    return form_example()
    # return test()


@app.route('/form-example', methods=['GET', 'POST']) #allow both GET and POST requests
def form_example():
    if request.method == 'POST': #this block is only entered when the form is submitted

        title = request.form.get('Title')
        timeEst = int(request.form.get('est'))
        DedLine = request.form.get('dead')

        setUp()
        createEvent(title, timeEst, DedLine)

    return render_template('index.html')



@app.route('/', methods=['GET','POST'])
def setUp():

    store = file.Storage('app/static/token.json')
    creds = store.get()

    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('app/static/credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)


@app.route('/', methods=['GET','POST'])
def getCalendarEvents(deadLine):
    store = file.Storage('app/static/token.json')
    creds = store.get()
    service = build('calendar', 'v3', http=creds.authorize(Http()))
    dueDate = deadLine

    d = datetime.datetime.utcnow()
    d = pytz.UTC.localize(d)
    pst = pytz.timezone('America/Chicago')
    nowUnformat = d.astimezone(pst).isoformat() + 'Z'
    now = nowUnformat[0:26] + nowUnformat[len(nowUnformat) - 1]
    print(now)

    dueDateFormatted = dueDate + 'T00:00:00-05:00'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                    timeMax = dueDateFormatted, singleEvents=True,
                                    orderBy = 'startTime').execute()

    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        # print(start, event['summary'])

    return events


@app.route('/', methods=['GET','POST'])
def findAvailableTimes(duration, deadLine):
    estTime = duration
    restrictStart = 23
    restrictEnd = 9

    availableTimes = []

    events = getCalendarEvents(deadLine)

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

        sameDay = (e1Day == e2Day)
        hourDiff = e2Hour - e1Hour
        minuteDiff = abs(e1Minute - e2Minute)
        checkRestrictStart = e1Hour - restrictStart

        if ((sameDay and ((hourDiff == estTime and minuteDiff >= 30) or (hourDiff > estTime))
                and ((checkRestrictStart >= estTime) or
                ((e1Hour - restrictEnd) >= estTime))) or
                ((not sameDay) and ((restrictStart - e1Hour) >= estTime))):

            startHour = e1Hour

            startMinute = e1Minute
            if startMinute >= 45:
                startHour += 1
                startMinute = 60 - startMinute
                startMinute = abs(startMinute - 15)
            else:
                startMinute += 15

            endHour = startHour + estTime
            endMinute = startMinute

            eventStart = formatDT2(e1Year, e1Month, e1Day, startHour, startMinute, e1Second)
            eventEnd = formatDT2(e1Year, e1Month, e1Day, endHour, endMinute, e1Second)

            timeSlot = [eventStart, eventEnd]
            availableTimes.append(timeSlot)
            print (len(availableTimes))
        # elif ((e1Day != e2Day) and  (restrictStart - e1Hour) >= estTime):
        #     eventStart = formatDT2(e1Year, e1Month, e1Day, e1Hour, e1Minute, e1Second)
        #     eventEnd = formatDT2(e1Year, e1Month, e1Day, e1Hour + estTime, e1Minute, e1Second)

    print(availableTimes)
    return availableTimes

@app.route('/', methods=['GET','POST'])
def getEventTime(duration, deadLine):
    availableTimes = findAvailableTimes(duration, deadLine)

    length = len(availableTimes)
    x = random.randrange(0, length)

    eventTime = availableTimes[x]
    return eventTime


@app.route('/')
def createEvent(newTitle, duration, deadLine):
    # global title

    eventTime = getEventTime(duration, deadLine)
    eventStart = eventTime[0]
    eventEnd = eventTime[1]
    event = {
        'summary': newTitle,
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
    print ('time: %s' % (eventStart))


@app.route('/', methods=['GET','POST'])
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


@app.route('/', methods=['GET','POST'])
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
