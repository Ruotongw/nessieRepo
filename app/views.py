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
import calendar
from .format import *
from .timeSlot import *

SCOPES = 'https://www.googleapis.com/auth/calendar'

@app.route('/', methods=['GET','POST'])
def main():

    global service
    try:
        print (service)
        return redirect('/form')
    except:
        if request.method == "POST":
            if request.headers.get('X-Requested-With'):

                auth_code = request.data
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

                return form()
        return render_template('base.html')



@app.route('/form', methods=['GET', 'POST']) #allow both GET and POST requests
def form():
    # print("we are in the form")
    # print(service)
    # redirect("/form")
    # render_template('index.html')
    try:
        # print (service)
        if request.method == 'POST': #this block is only entered when the form is submitted
            if not request.headers.get('X-Requested-With'):

                global title
                title = request.form.get('Title')

                global timeEst
                timeEst = int(request.form.get('est'))

                global deadLine
                deadLine = request.form.get('dead')
                addEvent()
            else:
                print ("else case")

        return render_template('index.html')
    except:
        return redirect('/')

@app.route('/allEvents', methods=['GET', 'POST'])
def getEvents():
    from datetime import date
    # '2018-11-30T11:25:00-05:00'
    # now = currentTime() #this is super temporary
    firstDay = str(date.today().year)+"-"+str(date.today().month)+"-01"
    numDay = calendar.monthrange(date.today().year, date.today().month)[1]
    lastDay= str(date.today().year)+"-"+str(date.today().month)+"-"+str(numDay)
    # print(firstDay)
    # print(lastDay)
    events = getCalendarEvents(firstDay + 'T00:00:00-06:00', lastDay) #replace deadline with something else
    eventsJSON = jsonify(events)
    eventsJSON.status_code = 200
    # print(eventsJSON)
    # redirect("/")
    return eventsJSON
    # return

def getCalendarEvents(min, max):
    '''Returns a list with every event on the user's primary Google Calendar
    from now unti the due date in cronological order. Each event is a dictionary.'''

    #this could be an issue since [min] is formatted and [max] is not
    # initDateFormatted = str(min) + 'T00:00:00-06:00'
    dueDateFormatted = str(max) + 'T00:00:00-06:00'
    events_result = service.events().list(calendarId='primary', timeMin=min,
                                    timeMax = dueDateFormatted, singleEvents=True,
                                    orderBy = 'startTime').execute()

    events = events_result.get('items', [])
    # print(events)
    if not events:
        print('No upcoming events found.')
    return events


def currentTime():
    print('in currentTime')
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

    global format
    format = Format()

    global timeSlot
    timeSlot = TimeSlot(timeEst)

    global availableTimes
    availableTimes = []

    openHours, openMinutes = openTimeWindow(workStart,workEnd)

    for i in range(len(events) - 1):
        event1 = events[i]
        event2 = events[i + 1]

        e1, e2 = format.formatEvent(event1, event2)

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
            print("before after")
            timeSlot = timeSlot.afterTimeSlot(e1)
            availableTimes.append(timeSlot)

        if(currentTime and (not sameDay and enoughTime2 and (e1.hour in openHours) and (timeWindow in openMinutes))):
            print("before after")
            timeSlot = timeSlot.afterTimeSlot(e1)
            availableTimes.append(timeSlot)

        if(not sameDay and enoughMorningTime):
            timeSlot = timeSlot.beforeTimeSlot(e2)
            availableTimes.append(timeSlot)

    # Accounts for the possible time slot after the last event before the due date.
    # Also accounts for if there's only one event before the due date.
    lastEvent = events[len(events) - 1]
    lastEnd, lastStart = format.formatEvent(lastEvent, lastEvent)
    print("lastEnd reached", lastEnd)

    secondToLast = events[len(events) - 2]
    secondEnd, secondStart = format.formatEvent(secondToLast, secondToLast)

    timeWindow = (lastEnd.hour * 60) + lastEnd.minute + (estTimeMin + 30)

    beforeTime = (lastStart.hour * 60 + lastStart.minute) - (workStart*60)
    enoughBeforeTime = (beforeTime >= estTimeMin + 30)

    timeDiff = (lastStart.hour * 60 + lastStart.minute) - (nowHour * 60 + nowMinute)
    enoughTime = (timeDiff >= (estTimeMin + 30))

    timeDiffEvent = (lastStart.hour * 60 + lastStart.minute) - (secondEnd.hour * 60 + secondEnd.minute)
    enoughTimeEvent = (timeDiffEvent >= (estTimeMin + 30))

    diffDays = lastStart.day != nowDay
    diffEventDays = lastStart.day != secondEnd.day

    if(enoughBeforeTime and (enoughTime or diffDays) and (diffEventDays or enoughTimeEvent)):
        timeSlot = timeSlot.beforeTimeSlot(lastStart)
        availableTimes.append(timeSlot)

    if((lastEnd.hour in openHours) and (timeWindow in openMinutes)):
        print("before after")
        timeSlot = timeSlot.afterTimeSlot(lastEnd)
        availableTimes.append(timeSlot)

    print(availableTimes)
    return availableTimes


def getEventTime():
    '''Returns a randomly selected time slot from all of the available times slots.
    If there are no time slots, it returns an exception instead of breaking.'''
    nowDay, nowHour, nowMinute = getNowDHM(currentTime())
    workStart = 6
    workEnd = 23
    now = currentTime()
    events = getCalendarEvents(now, deadLine)

    availableTimes = findAvailableTimes(nowDay, nowHour, nowMinute, workStart, workEnd, events)

    length = len(availableTimes)
    if (length != 0):
        # print (length)
        x = random.randrange(0, length)

        global timeSlot
        timeSlot = availableTimes[x]
        return timeSlot
    else:
        return  '''<h1>Oops</h1>'''

def rescheduleEvent():
    availableTimes.remove(timeSlot)
    timeSlot = getEventTime()
    return timeSlot

event = {}
def createEvent():
    '''Creates a Google Calendar event based on the randomly chosen time slot
    and adds it to the user's primary calendar.'''

    global event
    eventTime = getEventTime()

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

        # event = service.events().insert(calendarId = 'primary', body = event).execute()
        # print ('Event created: %s' % (event.get('summary')))
        # print ('time: %s' % (eventStart))
        # return redirect('https://calendar.google.com/calendar/', code=302)
        return event

    else:
        print("No available times")


def addEvent():
    event = createEvent()
    event = service.events().insert(calendarId = 'primary', body = event).execute()
    print ('Event created: %s' % (event.get('summary')))
    print ('time: %s' % (eventTime[0]))
    return redirect('https://calendar.google.com/calendar/', code=302)


def getScheduledEvent():
    global event
    return event


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
