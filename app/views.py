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

# credentials = 0
# Dedline = '2018-11-30T11:25:00-05:00'

@app.route('/', methods=['GET','POST'])
def main():

    global service
    print ("test")
    if request.method == "POST":
        print ("main data = ")
        print (request.data)
        if request.headers.get('X-Requested-With'):

            auth_code = request.data
            print (auth_code)
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

            now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

            # redirect(url_for('form'))
            return form()

    return render_template('newIndex.html')


@app.route('/form', methods=['GET', 'POST']) #allow both GET and POST requests
def form():
    print("we are in the form")
    print(service)
    # redirect("/form")
    # render_template('index.html')
    if request.method == 'POST': #this block is only entered when the form is submitted
        if not request.headers.get('X-Requested-With'):

            global title
            title = request.form.get('Title')

            global timeEst
            timeEst = int(request.form.get('est'))

            global deadLine
            deadLine = request.form.get('dead')
            print (deadLine)
            print ('phase 1')
            # setUp()
            createEvent()
        else:
            print ("else case")
            # render_template('newIndex.html')
    return render_template('newIndex.html')


def getCalendarEvents():
    '''Returns a list with every event on the user's primary Google Calendar
    from now unti the due date in cronological order. Each event is a dictionary.'''

    # store = file.Storage('app/static/token.json')
    # creds = store.get()
    # http_auth = credentials.authorize(httplib2.Http())
    # service = discovery.build('calendar', 'v3', http=http_auth)
    now = currentTime()

    dueDateFormatted = str(deadLine) + 'T00:00:00-06:00'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                    timeMax = dueDateFormatted, singleEvents=True,
                                    orderBy = 'startTime').execute()

    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    return events


def currentTime():
    '''Returns the current Chicago time, accounting for daylight savings and
    in the correct string format to use with Google's API.'''

    chi = timezone('America/Chicago')
    fmt = '%Y-%m-%dT%H:%M:%S%z'

    utcDt = datetime.datetime.utcnow()
    localDt = utcDt.replace(tzinfo=chi)
    localDt.strftime(fmt)

    # Offsets the time from UTC to Chicago
    offset = localDt - datetime.timedelta(hours = 5)
    offset.strftime(fmt)

    now = chi.normalize(offset)

    # Formats and adds necessary colon
    now = now.strftime(fmt)
    now = now[:22] + ':' + now[22:]

    return now

def findAvailableTimes(nowDay, nowHour, nowMinute, workStart, workEnd, events):
    '''Calculates every available time slot in relation to the events on the user's
    calender from now until the assignment due date. Returns a list of these time slots.'''

    estTimeMin = timeEst * 60
    estMins = estTimeMin % 60
    estHours = (estTimeMin - estMins) / 60

    availableTimes = []

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

        if(currentTime and (sameDay and enoughTime and (e1.hour in openHours) and (timeWindow in openMinutes))):
            timeSlot = generalTimeSlot(e1)
            availableTimes.append(timeSlot)

        if(currentTime and (not sameDay and enoughTime2 and (e1.hour in openHours) and (timeWindow in openMinutes))):
            timeSlot = generalTimeSlot(e1)
            availableTimes.append(timeSlot)

        if(not sameDay and enoughMorningTime):
            timeSlot = morningTimeSlot(e2)
            availableTimes.append(timeSlot)

    # Accounts for the possible time slot after the last event before the due date.
    # Also accounts for if there's only one event before the due date.
    lastEvent = events[len(events) - 1]
    lastEnd, lastStart = formatEvent(lastEvent, lastEvent)

    timeWindow = (lastEnd.hour * 60) + lastEnd.minute + (estTimeMin + 30)

    beforeTime = (lastStart.hour * 60 + lastStart.minute) - (workStart*60)
    enoughBeforeTime = beforeTime >= estTimeMin + 30

    timeDiff = (lastStart.hour * 60 + lastStart.minute) - (nowHour * 60 + nowMinute)
    enoughTime = timeDiff >= (estTimeMin + 30)

    diffDays = lastStart.day != nowDay

    if(enoughBeforeTime and (enoughTime or diffDays)):
        timeSlot = morningTimeSlot(lastStart)
        availableTimes.append(timeSlot)

    if((lastEnd.hour in openHours) and (timeWindow in openMinutes)):
        timeSlot = generalTimeSlot(lastEnd)
        availableTimes.append(timeSlot)

    print(availableTimes)
    return availableTimes


def getEventTime():
    '''Returns a randomly selected time slot from all of the available times slots.
    If there are no time slots, it returns an exception instead of breaking.'''
    nowDay, nowHour, nowMinute = getNowDHM(currentTime())
    workStart = 6
    workEnd = 23
    events = getCalendarEvents()

    availableTimes = findAvailableTimes(nowDay, nowHour, nowMinute, workStart, workEnd, events)

    length = len(availableTimes)
    if (length != 0):
        # print (length)
        x = random.randrange(0, length)

        eventTime = availableTimes[x]
        return eventTime
    else:
        return  '''<h1>Oops</h1>'''


event = {}
def createEvent():
    '''Creates a Google Calendar event based on the randomly chosen time slot
    and adds it to the user's primary calendar.'''

    print ('phase 2')

    global event
    eventTime = getEventTime()

    # print(eventTime)

    if (eventTime != '''<h1>Oops</h1>'''):
        eventStart = eventTime[0]
        eventEnd = eventTime[1]
        event = {
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


# def credentials_to_dict(credentials):
#   return {'token': credentials.token,
#           'refresh_token': credentials.refresh_token,
#           'token_uri': credentials.token_uri,
#           'client_id': credentials.client_id,
#           'client_secret': credentials.client_secret,
#           'scopes': credentials.scopes}


# The following are helper functions for findAvailableTimes()

def getNowDHM(currentTime):
    currentTime = currentTime[:22] + currentTime[23:]
    currentTime = datetime.datetime.strptime(currentTime, '%Y-%m-%dT%H:%M:%S%z')

    nowDay = currentTime.day
    nowHour = currentTime.hour
    nowMinute = currentTime.minute
    return nowDay, nowHour, nowMinute


def openTimeWindow(openStartTime, openEndTime):
    '''Returns the time during the day when the user can work on assignments
    in terms of hours and in terms of the minutes out of the entire minutes
    in a day.'''

    openHours = range(openStartTime, openEndTime)
    openMinutes = range(openStartTime * 60, openEndTime * 60)
    return openHours, openMinutes


def formatEvent(event1, event2):
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


def morningTimeSlot(event2):
    '''Returns the time slot before event2. Used for the first event of the day,
    given that there is enough time between that event and the start of working
    hours.'''

    localizedTime = timeEst

    event2Min = (event2.hour * 60) + event2.minute
    localizedTime = localizedTime * 60

    startTime = event2Min - localizedTime - 15
    startMin = startTime % 60
    startHour = (startTime - startMin) / 60

    endTime = event2Min -15
    endMin = endTime % 60
    endHour = (endTime - endMin)/60

    eventStart = formatDT2(event2.year, event2.month, event2.day, startHour, startMin, event2.second)
    eventEnd = formatDT2(event2.year, event2.month, event2.day, endHour, endMin, event2.second)

    timeSlot = [eventStart, eventEnd]
    return timeSlot


def generalTimeSlot(event1):
    '''Returns the time slot after event1. Used for most scheduling cases, hence
    the name generalTimeSlot.'''
    localizedTime = timeEst

    event1Min = (event1.hour * 60) + event1.minute
    localizedTime = localizedTime * 60

    startTime = event1Min + 15
    startMin = startTime % 60
    startHour = (startTime - startMin) / 60

    endTime = startTime + localizedTime
    endMin = endTime % 60
    endHour = (endTime - endMin)/60

    eventStart = formatDT2(event1.year, event1.month, event1.day, startHour, startMin, event1.second)
    eventEnd = formatDT2(event1.year, event1.month, event1.day, endHour, endMin, event1.second)

    timeSlot = [eventStart, eventEnd]
    return timeSlot


def formatDT1(dt):
    '''Returns a datetime string of the given datetime object formatted
    correctly for the Google API.'''

    fmt = '%Y-%m-%dT%H:%M:%S%z'
    dt = dt.strftime(fmt)
    dt = dt[:22] + ':' + e2[22:]

    return dt


def formatDT2(year, month, day, hour, minute, second):
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
