# views.py

from __future__ import print_function
from apiclient import discovery
import httplib2
from flask import render_template, Flask, request, json, redirect, url_for, jsonify
import os
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import google.oauth2.credentials
from app import app
import datetime
import random
import math
import pytz


SCOPES = 'https://www.googleapis.com/auth/calendar'


# store = file.Storage('app/static/token.json')
# creds = store.get()
# service = build('calendar', 'v3', http=creds.authorize(Http()))

nowDay = 0
nowHour = 0
nowMinute = 0
credentials = 0
global Dedline
# @app.route('/form', methods=['GET', 'POST']) #allow both GET and POST requests
def form(credentials):
    print("test")
    # redirect("/form")
    # render_template('index.html')
    if request.method == 'POST': #this block is only entered when the form is submitted
        if not request.headers.get('X-Requested-With'):

            title = request.form.get('Title')
            timeEst = int(request.form.get('est'))
            DedLine = request.form.get('dead')

            # setUp()
            createEvent(title, timeEst, DedLine, credentials)
    return render_template('newIndex.html')

@app.route('/', methods=['GET','POST'])
def main():


    if request.method == "POST":
        if request.headers.get('X-Requested-With'):
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
            # form(credentials)
            now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

            # redirect(url_for('form'))
            return form(credentials)
    return render_template('newIndex.html')

# def setUp():

    # store = file.Storage('app/static/token.json')
    # creds = store.get()
    #
    # if not credentials or credentials.invalid:
    #     flow = client.flow_from_clientsecrets('app/static/credentials.json', SCOPES)
    #     credentials = tools.run_flow(flow, store)



def getCalendarEvents(deadLine, credentials):
    global nowDay
    global nowHour
    global nowMinute

    # store = file.Storage('app/static/token.json')
    # creds = store.get()
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http_auth)
    dueDate = deadLine

    # Changes 'now' from UTC time to Central Time and formats it correctly
    d = datetime.datetime.utcnow()
    d = pytz.UTC.localize(d)
    pst = pytz.timezone('America/Chicago')

    nowUnformat = d.astimezone(pst)

    # Used later in the algorithm
    nowDay = nowUnformat.day
    nowHour = nowUnformat.hour
    nowMinute = nowUnformat.minute

    nowString = nowUnformat.isoformat() + 'Z'

    now = nowString[0:26] + nowString[len(nowString) - 1]
    print(now)

    dueDateFormatted = str(dueDate) + 'T00:00:00-05:00'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                    timeMax = dueDateFormatted, singleEvents=True,
                                    orderBy = 'startTime').execute()

    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')

    return events

@app.route('/allEvents/', methods=['GET','POST'])
def getDisplayEvents():
    events= getCalendarEvents(DedLine)
    eventsJSON = jsonify(events)
    eventsJSON.status_code = 200
    print(eventsJSON)
    return eventsJSON




def findAvailableTimes(duration, deadLine, credentials):
    global nowDay
    global nowHour
    global nowMinute

    estTimeMin = duration * 60

    estMins = estTimeMin % 60
    estHours = (estTimeMin - estMins) / 60

    # Eventually these values will be taken as user input
    openStartTime = 6
    openEndTime = 23

    availableTimes = []

    events = getCalendarEvents(deadLine, credentials)

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

        # For events on the same day
        timeDiff = (e2Hour * 60 + e2Minute) - (e1Hour * 60 + e1Minute)
        enoughTime = timeDiff >= (estTimeMin + 30)

        # For events on different days
        timeDiff2 = (1440 - (e1Hour * 60) + e1Minute) + (e2Hour * 60 + e2Minute)
        enoughTime2 = timeDiff2 >= (estTimeMin + 30)

        # Ensures that the algorithm doesn't schedule events in the past
        currentTime = ((e1Hour == nowHour) and (e1Minute >= nowMinute)) or e1Hour > nowHour or (e1Day > nowDay)

        # Ensures that the entire scheduled event would be within the open working hours
        timeWindow = (e1Hour * 60) + e1Minute + (estTimeMin + 30)

        openRangeH = range(openStartTime, openEndTime)
        openRangeM = range(openStartTime * 60, openEndTime * 60)

        if(currentTime and (sameDay and enoughTime and (e1Hour in openRangeH) and (timeWindow in openRangeM))
                or (not sameDay and enoughTime2 and (e1Hour in openRangeH) and (timeWindow in openRangeM))):

            startHour = e1Hour

            print(startHour)

            startMinute = e1Minute
            if startMinute + estMins >= 45:
                startHour += 1
                startMinute = 60 - startMinute
                startMinute = abs(startMinute - 15)
            else:
                startMinute += 15

            print(startMinute)

            endHour = startHour + estHours

            print(endHour)

            endMinute = startMinute + estMins

            print(endMinute)

            eventStart = formatDT2(e1Year, e1Month, e1Day, startHour, startMinute, e1Second)

            print(eventStart)

            eventEnd = formatDT2(e1Year, e1Month, e1Day, endHour, endMinute, e1Second)

            print(eventEnd)

            timeSlot = [eventStart, eventEnd]
            availableTimes.append(timeSlot)
            print (len(availableTimes))

    print(availableTimes)
    return availableTimes

def getEventTime(duration, deadLine, credentials):
    availableTimes = findAvailableTimes(duration, deadLine, credentials)

    length = len(availableTimes)
    if (length != 0):
        print (length)
        x = random.randrange(0, length)

        eventTime = availableTimes[x]
        return eventTime
    else:
        return  '''<h1>Oops</h1>'''

event = {}
def createEvent(newTitle, duration, deadLine, credentials):
    global event
    eventTime = getEventTime(duration, deadLine)

    print(eventTime)

    if (eventTime != '''<h1>Oops</h1>'''):
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

        print(event)

        event = service.events().insert(calendarId='primary', body=event).execute()
        print ('Event created: %s' % (event.get('summary')))
        print ('time: %s' % (eventStart))
        return redirect('https://calendar.google.com/calendar/', code=302)

    else:
        print("No available times")



def getScheduledEvent():
    global event
    return event

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

    hour = int(hour)
    hour = hour.__str__()
    if int(hour) < 10:
        hour = '0' + hour

    minute = int(minute)
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
