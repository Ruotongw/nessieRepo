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
from .now import *

SCOPES = 'https://www.googleapis.com/auth/calendar'

@app.route('/', methods=['GET','POST'])
def main():

    global workStart
    global workEnd
    # global eventSlot

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
    try:
        print (service)
        if request.method == 'POST': #this block is only entered when the form is submitted
            if not request.headers.get('X-Requested-With'):

                global title
                title = request.form.get('Title')

                global timeEst
                timeEst = int(request.form.get('est'))

                global deadLine
                deadLine = request.form.get('dead')

                global rep
                rep = int(request.form.get('rep'))
                createEvent()
                return redirect('/popup')
                # print("event added")
                # redirect('/popup')
                # maybe move the add event to a new route
            else:
                print ("else case")

        return render_template('index.html')
    except:
        return redirect('/')

@app.route('/popup', methods=['GET', 'POST'])
def popup():
    try:
        print (event)
        return render_template('popup.html', event=event)
    except:
        return redirect("/form")

@app.route('/allEvents', methods=['GET', 'POST'])
def getEvents():
    from datetime import date
    # '2018-11-30T11:25:00-05:00'
    firstDay = str(date.today().year)+"-"+str(date.today().month)+"-01"
    numDay = calendar.monthrange(date.today().year, date.today().month)[1]
    lastDay= str(date.today().year)+"-"+str(date.today().month)+"-"+str(numDay)
    events = getCalendarEvents(firstDay + 'T00:00:00-06:00', lastDay) #replace deadline with something else
    eventsJSON = jsonify(events)
    eventsJSON.status_code = 200
    # print(eventsJSON)
    # redirect("/")
    return eventsJSON


def getCalendarEvents(min, max):
    '''Returns a list with every event on the user's primary Google Calendar
    from now unti the due date in cronological order. Each event is a dictionary.'''

    #this could be an issue since [min] is formatted and [max] is not
    dueDateFormatted = str(max) + 'T00:00:00-06:00'
    events_result = service.events().list(calendarId='primary', timeMin=min,
                                    timeMax = dueDateFormatted, singleEvents=True,
                                    orderBy = 'startTime').execute()

    events = events_result.get('items', [])
    if not events:
        print('No upcoming events found.')
    return events


def findAvailableTimes(nowDay, nowHour, nowMinute, workStart, workEnd, events):
    '''Calculates every available time slot in relation to the events on the user's
    calender from now until the assignment due date. Returns a list of these time slots.'''

    global format
    format = Format()
    global timeSlot
    timeSlot = TimeSlot(timeEst)

    for i in range(len(events) - 1):
        event1 = events[i]
        event2 = events[i + 1]
        e1, e2 = format.formatEvent(event1, event2)
        compareEvents(e1, e2, workStart, workEnd, nowDay, nowHour, nowMinute)

    lastEvent = events[len(events) - 1]
    secondToLast = events[len(events) - 2]
    compareLastEvent(lastEvent, secondToLast, workStart, workEnd, nowDay, nowHour, nowMinute)

    # print(availableTimes)
    return availableTimes


def compareLastEvent(lastEvent, secondToLast, workStart, workEnd, nowDay, nowHour, nowMinute):
    '''Accounts for finding the time slots around the the last event before the
    deadline. Also accounts for if there is only one event before the deadline.'''

    estTimeMin = timeEst * 60
    estMins = estTimeMin % 60
    estHours = (estTimeMin - estMins) / 60
    openHours, openMinutes = openTimeWindow(workStart, workEnd)

    lastEnd, lastStart = format.formatEvent(lastEvent, lastEvent)
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
        time = timeSlot.beforeTimeSlot(lastStart)
        availableTimes.append(time)

    if((lastEnd.hour in openHours) and (timeWindow in openMinutes)):
        time = timeSlot.afterTimeSlot(lastEnd)
        availableTimes.append(time)


def compareEvents(e1, e2, workStart, workEnd, nowDay, nowHour, nowMinute):
    '''Compares each pair of events on the user's calendar from now until the
    entered deadline. If there is enough time between the events, the time slot
    between them is added to the list of available times.'''

    estTimeMin = timeEst * 60
    estMins = estTimeMin % 60
    estHours = (estTimeMin - estMins) / 60
    openHours, openMinutes = openTimeWindow(workStart, workEnd)

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
    now = ((e1.hour == nowHour) and (e1.minute >= nowMinute)) or e1.hour > nowHour or (e1.day > nowDay)

    # Ensures that the entire scheduled event would be within the open working hours
    timeWindow = (e1.hour * 60) + e1.minute + (estTimeMin + 30)

    if(now and (sameDay and enoughTime and (e1.hour in openHours) and (timeWindow in openMinutes))):
        time = timeSlot.afterTimeSlot(e1)
        availableTimes.append(time)

    if(now and (not sameDay and enoughTime2 and (e1.hour in openHours) and (timeWindow in openMinutes))):
        time = timeSlot.afterTimeSlot(e1)
        availableTimes.append(time)

    if(not sameDay and enoughMorningTime):
        time = timeSlot.beforeTimeSlot(e2)
        availableTimes.append(time)


def getEventTime(availableTimes):
    '''Returns a randomly selected time slot from all of the available times slots.
    If there are no time slots, it returns an exception instead of breaking.'''

    length = len(availableTimes)
    if (length != 0):
        x = random.randrange(0, length)
        # print("length:",length)
        # print("x",x)

        global eventSlot
        eventSlot = availableTimes[x]
        # print("global in get event time, ", globals())
        # print("local in get event time, ", locals())
        return eventSlot
    else:
        return  '''<h1>Oops</h1>'''

def reassignSlot(start, end):
    global eventSlot
    eventSlot = [start,end]
    # print("reassign eventSlot:",eventSlot)
    # print("global in reassignSlot, ", globals())
    return eventSlot

@app.route('/reschedule', methods=['GET', 'POST'])
def rescheduleEvent():
    # print("availableTimes ",availableTimes)
    # print("eventSlot", eventSlot)
    availableTimes.remove(eventSlot)

    length = len(availableTimes)
    if (length != 0):
        x = random.randrange(0, length)
        # print(x)
        eventTime = availableTimes[x]

        eventStart = eventTime[0]
        eventEnd = eventTime[1]
        reassignSlot(eventStart, eventEnd)
        # print("post ", eventSlot)
        global event
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
        return redirect('/popup')
    else:
        print("No available times")
#no return statement!


def createEvent():
    global rep
    '''Creates a Google Calendar event based on the randomly chosen time slot
    and prepares it to be added to the user's calendar.'''

    global current
    current = Now()
    global availableTimes
    availableTimes = []

    now = current.currentTime()
    nowDay, nowHour, nowMinute = current.getNowDHM(now)
    workStart = 6
    workEnd = 23
    events = getCalendarEvents(now, deadLine)

    workStart = workStart + 1
    availableTimes = findAvailableTimes(nowDay, nowHour, nowMinute, workStart, workEnd, events)

    if rep == 1:
        global event
        eventTime = getEventTime(availableTimes)

        if (eventTime != '''<h1>Oops</h1>'''):
            event =  eventFormat(eventTime)
            return event

        else:
            print("No available times")

    else:
        global chosenTimeSlots
        formattedChosenOnes = []
        divisionOfTimeSlots()
        selectionOfTimeSlots()

        for i in range(len(chosenTimeSlots)):
            formattedChosenOnes.append(eventFormat(chosenTimeSlots[i]))
        print (formattedChosenOnes)
        for i in range(len(formattedChosenOnes)):
            add = service.events().insert(calendarId = 'primary', body = formattedChosenOnes[i]).execute()
            print (formattedChosenOnes[i])
        return formattedChosenOnes

def eventFormat(eventTime):

    eventStart = eventTime[0]
    eventEnd = eventTime[1]
    formattedEvent = {
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
    return formattedEvent


def divisionOfTimeSlots():
    global availableTimes
    global dividedTimeSlots
    dividedTimeSlots = []

    length = len(availableTimes)
    size = length // rep

    for i in range(rep - 1):
        times = availableTimes[i * size: ((i + 1) * size)]
        dividedTimeSlots.append(times)
    dividedTimeSlots.append(availableTimes[((rep - 1) * size): length])
    return dividedTimeSlots

def selectionOfTimeSlots():
    global chosenTimeSlots
    chosenTimeSlots = []
    for i in range(rep):
        chosenTimeSlots.append(getEventTime(dividedTimeSlots[i]))
    return chosenTimeSlots


@app.route('/add', methods=['GET', 'POST'])
def addEvent():
    '''Adds chosen event to the user's calendar.'''

    # event = createEvent()
    add = service.events().insert(calendarId = 'primary', body = event).execute()
    print ('Event created: %s' % (event.get('summary')))
    # print ('time: %s' % (eventTime[0]))
    return redirect('/form')
    # return redirect('https://calendar.google.com/calendar/', code=302)


def getScheduledEvent():
    return event


def openTimeWindow(openStartTime, openEndTime):
    '''Returns the time during the day when the user can work on assignments
    in terms of hours and in terms of the minutes out of the entire minutes
    in a day.'''

    openHours = range(openStartTime, openEndTime)
    openMinutes = range(openStartTime * 60, openEndTime * 60)
    return openHours, openMinutes
