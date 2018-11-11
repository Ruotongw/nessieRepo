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
from pytz import timezone
import time
from tzlocal import get_localzone


SCOPES = 'https://www.googleapis.com/auth/calendar'


# store = file.Storage('app/static/token.json')
# creds = store.get()
# service = build('calendar', 'v3', http=creds.authorize(Http()))

credentials = 0
# Dedline = '2018-11-30T11:25:00-05:00'

@app.route('/', methods=['GET','POST'])
def main():

    if request.method == "POST":
        print ("main data = ")
        print (request.data)
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

@app.route('/', methods=['GET', 'POST']) #allow both GET and POST requests
def form(credentials):
    print("we are in the form")
    # redirect("/form")
    # render_template('index.html')
    if request.method == 'POST': #this block is only entered when the form is submitted
        if not request.headers.get('X-Requested-With'):

            title = request.form.get('Title')
            timeEst = int(request.form.get('est'))
            DedLine = request.form.get('dead')
            print ('phase 1')
            # setUp()
            createEvent(title, timeEst, DedLine, credentials)
        else:
            print ("else case")
            # render_template('newIndex.html')
    return render_template('newIndex.html')


# def setUp():

    # store = file.Storage('app/static/token.json')
    # creds = store.get()
    #
    # if not credentials or credentials.invalid:
    #     flow = client.flow_from_clientsecrets('app/static/credentials.json', SCOPES)
    #     credentials = tools.run_flow(flow, store)



def getCalendarEvents(deadLine, credentials):
    # store = file.Storage('app/static/token.json')
    # creds = store.get()
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http_auth)
    dueDate = deadLine

    now = currentTime()

    dueDateFormatted = str(dueDate) + 'T00:00:00-06:00'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                    timeMax = dueDateFormatted, singleEvents=True,
                                    orderBy = 'startTime').execute()

    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    print (events)
    return events

def currentTime():
    chi = timezone('America/Chicago')
    fmt = '%Y-%m-%dT%H:%M:%S%z'

    # Retrieves the current time in UTC time, converts it to Chicago time,
    # and formats it
    utcDt = datetime.datetime.utcnow()
    # localDt = utcDt.astimezone(chi)
    localDt = utcDt.replace(tzinfo=chi)
    localDt.strftime(fmt)

    # Offsets the time from UTC to Chicago
    offset = localDt - datetime.timedelta(hours = 5)
    offset.strftime(fmt)

    # Normalizes it to change the offset depending on DST
    now = chi.normalize(offset)
    # Formats and adds necessary colon
    now = now.strftime(fmt)
    now = now[:22] + ':' + now[22:]
    return now

def getNowDHM(currentTime):
    nowDay = currentTime.day
    nowHour = currentTime.hour
    nowMinute = currentTime.minute
    return nowDay, nowHour, nowMinute


@app.route('/allEvents/', methods=['GET','POST'])
def getDisplayEvents():
    print ("SOS")
    # events= getCalendarEvents('2018-11-30T11:25:00-05:00')
    eventsJSON = jsonify('2018-11-30T11:25:00-05:00')
    eventsJSON.status_code = 200
    print(eventsJSON)
    redirect("/")
    return eventsJSON

def openTimeWindow(openStartTime, openEndTime):
    openHours = range(openStartTime, openEndTime)
    openMinutes = range(openStartTime * 60, openEndTime * 60)
    return openHours, openMinutes

def getOpenStartTime():
    openStartTime=6
    return openStartTime

def formatEvent(event1, event2):
    fmt = '%Y-%m-%dT%H:%M:%S%z'

    e1str = event1['end'].get('dateTime')
    e2str = event2['start'].get('dateTime')

    e1str = e1str[:22] + e1str[23:]
    e2str = e2str[:22] + e2str[23:]

    e1 = datetime.datetime.strptime(e1str, fmt)
    e2 = datetime.datetime.strptime(e2str, fmt)

    utc = timezone('UTC')
    chi = timezone('America/Chicago')

    # e1 = e1.astimezone(utc)
    # e2 = e2.astimezone(utc)

    e1 = e1.replace(tzinfo=utc)
    e2 = e2.replace(tzinfo=utc)

    e1.strftime(fmt)
    e2.strftime(fmt)

    e1, e2 = inDaylightSavings(e1, e2)

    e1.strftime(fmt)
    e2.strftime(fmt)

    e1 = chi.normalize(e1)
    e2 = chi.normalize(e2)

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

def morningTimeSlot(event2, duration):
    event2Min = (event2.hour * 60) + event2.minute
    duration = duration * 60

    startTime = event2Min - duration - 15
    startMin = startTime % 60
    startHour = (startTime - startMin) / 60

    endTime = event2Min -15
    endMin = endTime % 60
    endHour = (endTime - endMin)/60

    eventStart = formatDT2(e2.year, e2.month, e2.day, startHour, startMin, e2.second)
    eventEnd = formatDT2(e2.year, e2.month, e2.day, endHour, endMin, e2.second)

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

    eventStart = formatDT2(e1.year, e1.month, e1.day, startHour, startMin, e1.second)
    eventEnd = formatDT2(e1.year, e1.month, e1.day, endHour, endMin, e1.second)

    timeSlot = [eventStart, eventEnd]
    return timeSlot


def findAvailableTimes(duration, deadLine, nowDay, nowHour, nowMinute, workStart, workEnd, events):

    estTimeMin = duration * 60
    estMins = estTimeMin % 60
    estHours = (estTimeMin - estMins) / 60

    availableTimes = []

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

        # openHours = range(openStartTime, openEndTime)
        # openMinutes = range(openStartTime * 60, openEndTime * 60)
        openHours, openMinutes = openTimeWindow(workStart,workEnd)

        if(currentTime and (sameDay and enoughTime and (e1.hour in openHours) and (timeWindow in openMinutes))
                or (not sameDay and enoughTime2 and (e1.hour in openHours) and (timeWindow in openMinutes))):
            timeSlot = generalTimeSlot(e1, duration)
            availableTimes.append(timeSlot)

        else if(not sameDay and not enoughTime2 and (timeWindow not in openMinutes) and enoughMorningTime):
            timeSlot = morningTimeSlot(e2, duration)
            availableTimes.append(timeSlot)

    # print (len(availableTimes))
    print(availableTimes)
    return availableTimes

def getEventTime(duration, deadLine, credentials):
    nowDay, nowHour, nowMinute = getNowDHM(currentTime())
    workStart = 6
    workEnd = 23
    events = getCalendarEvents(deadLine, credentials)

    availableTimes = findAvailableTimes(duration, deadLine, nowDay, nowHour, nowMinute, workStart, workEnd, events)

    length = len(availableTimes)
    if (length != 0):
        # print (length)
        x = random.randrange(0, length)

        eventTime = availableTimes[x]
        return eventTime
    else:
        return  '''<h1>Oops</h1>'''

event = {}
def createEvent(newTitle, duration, deadLine, credentials):

    print ('phase 2')

    global event
    eventTime = getEventTime(duration, deadLine)

    # print(eventTime)

    if (eventTime != '''<h1>Oops</h1>'''):
        eventStart = eventTime[0]
        eventEnd = eventTime[1]
        event = {
            'summary': newTitle,
            'start': {
                'dateTime': eventStart,
                'timeZone': 'America/Chicago',
            },
            'end': {
                'dateTime': eventEnd,
                'timeZone': 'America/Chicago'
            },
        }

        print(event)

        event = service.events().insert(calendarId = 'primary', body = event).execute()
        print ('Event created: %s' % (event.get('summary')))
        print ('time: %s' % (eventStart))
        return redirect('https://calendar.google.com/calendar/', code=302)

    else:
        print("No available times")



def getScheduledEvent():
    global event
    return event

def formatDT1(dt):
    fmt = '%Y-%m-%dT%H:%M:%S%z'
    dt = dt.strftime(fmt)
    dt = dt[:22] + ':' + e2[22:]

    return dt

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


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
