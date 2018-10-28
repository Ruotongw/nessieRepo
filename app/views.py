# views.py

from __future__ import print_function
from apiclient import discovery
import httplib2
from flask import render_template, Flask, request, json, redirect, url_for
import os
import requests
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import google.oauth2.credentials
import google_auth_oauthlib.flow
from app import app
import random
import math

@app.route("/form", methods=['GET', 'POST']) #allow both GET and POST requests
def form():
    print("test")
    render_template('index.html')
    print("test")
    redirect("/form")
    render_template('index.html')
    if request.method == 'POST': #this block is only entered when the form is submitted

        title = request.form.get('Title')
        timeEst = int(request.form.get('est'))
        DedLine = request.form.get('dead')

        setUp()
        createEvent(title, timeEst, DedLine)
    return render_template('index.html')
    return render_template('index.html')

@app.route('/', methods=['GET','POST'])
def main():


    # render_template('base.html')
    if request.method == "POST":
        auth_code = request.data
        print (auth_code)
        if not request.headers.get('X-Requested-With'):
            print ('403')

        # Set path to the Web application client_secret_*.json file you downloaded from the
        # Google API Console: https://console.developers.google.com/apis/credentials
        CLIENT_SECRET_FILE = 'app/static/client_secret.json'

        # Exchange auth code for access token, refresh token, and ID token
        credentials = client.credentials_from_clientsecrets_and_code(
            CLIENT_SECRET_FILE,
            ['https://www.googleapis.com/auth/calendar', 'profile', 'email'],
            auth_code)

        # Call Google API
        http_auth = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http_auth)

        # Get profile info from ID token
        # userid = credentials.id_token['sub']
        # email = credentials.id_token['email']

        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        return redirect(url_for('form'))
    return render_template('base.html')

def setUp():

    store = file.Storage('app/static/token.json')
    creds = store.get()

    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('app/static/credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)


def getCalendarEvents(deadLine):
    store = file.Storage('app/static/token.json')
    creds = store.get()
    service = build('calendar', 'v3', http=creds.authorize(Http()))
    dueDate = deadLine

    now = datetime.datetime.utcnow().isoformat() + 'Z'

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

def getEventTime(duration, deadLine):
    availableTimes = findAvailableTimes(duration, deadLine)

    length = len(availableTimes)
    if (len != 0):
        print (length)
        x = random.randrange(0, length)

        eventTime = availableTimes[x]
        return eventTime
    else:
        main()

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

    print ('Event created: %s' % (event.get('summary')))
    print ('time: %s' % (eventStart))


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

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


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
