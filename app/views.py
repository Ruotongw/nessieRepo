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
from .findTime import *

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
    print("in popup")
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



def getEventTime(availableTime):
    '''Returns a randomly selected time slot from all of the available times slots.
    If there are no time slots, it returns an exception instead of breaking.'''


    length = len(availableTime)
    if (length != 0):
        x = random.randrange(0, length)

        global eventSlot
        eventSlot = availableTime[x]

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
    availableTime.remove(eventSlot)

    length = len(availableTime)
    if (length != 0):
        x = random.randrange(0, length)
        eventTime = availableTime[x]

        eventStart = eventTime[0]
        eventEnd = eventTime[1]
        reassignSlot(eventStart, eventEnd)

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

    global format
    format = Format()

    global availableTimes
    availableTimes = FindTime()
    global availableTime
    availableTime = []

    now = current.currentTime()
    nowDay, nowHour, nowMinute = current.getNowDHM(now)
    workStart = 6
    workEnd = 23
    events = getCalendarEvents(now, deadLine)

    workStart = workStart + 1
    availableTime = availableTimes.findAvailableTimes(nowDay, nowHour, nowMinute, workStart, workEnd, events, timeEst)

    if rep == 1:
        global event
        eventTime = getEventTime(availableTime)

        if (eventTime != '''<h1>Oops</h1>'''):
            event =  format.eventFormatDictionary(eventTime, title)
            return event

        else:
            print("No available times")

    else:
        global chosenTimeSlots
        formattedChosenOnes = []
        divisionOfTimeSlots()
        selectionOfTimeSlots()

        for i in range(len(chosenTimeSlots)):
            formattedChosenOnes.append(format.eventFormatDictionary(chosenTimeSlots[i], title))
        print (formattedChosenOnes)
        for i in range(len(formattedChosenOnes)):
            add = service.events().insert(calendarId = 'primary', body = formattedChosenOnes[i]).execute()
            print (formattedChosenOnes[i])
        return formattedChosenOnes


def divisionOfTimeSlots():
    global dividedTimeSlots
    dividedTimeSlots = []

    length = len(availableTime)
    size = length // rep

    for i in range(rep - 1):
        times = availableTime[i * size: ((i + 1) * size)]
        dividedTimeSlots.append(times)
    dividedTimeSlots.append(availableTime[((rep - 1) * size): length])
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
