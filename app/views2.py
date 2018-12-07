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
from .time import *
from .findTime import *

SCOPES = 'https://www.googleapis.com/auth/calendar'

@app.route('/', methods=['GET','POST'])
def main():

    global workStart
    global workEnd
    # global eventSlot
    global current
    current = Time()

    global format
    format = Format()

    global findTime
    findTime = FindTime()

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

                return createEvent()
                # return redirect('/popup')
                # print("event added")
                # redirect('/popup')
                # maybe move the add event to a new route
            else:
                print ("else case")

        return render_template('index.html')
    except:
        return redirect('/')

# @app.route('/form2', methods=['GET', 'POST'])
# def form2():
#     try:
#         print (service)
#         if request.method == 'POST': #this block is only entered when the form is submitted
#
#             if not request.headers.get('X-Requested-With'):
#
#                 global earliestWorkTime
#                 earliestWorkTime = request.form.get('earliest')
#
#                 global latestWorkTime
#                 latestWorkTime = request.form.get('latest')
#
#             else:
#                 print("else statement")
#
#         return render_template('index.html')
#     except:
#         return redirect('/')

@app.route('/popup', methods=['GET', 'POST'])
def popup():
    print("in popup")
    try:
        print (formattedChosenOnes)
        return render_template('popup.html', event=formattedChosenOnes[0])
    except:
        return redirect("/form")

@app.route('/allEvents', methods=['GET', 'POST'])
def getEvents():
    from datetime import date
    # '2018-11-30T11:25:00-05:00'
    # print(request.args)
    year = request.args.get('year')
    month = request.args.get('month')
    # firstDay = str(date.today().year)+"-"+str(date.today().month)+"-01"
    firstDay = str(year)+"-"+str(month)+"-01"
    numDay = calendar.monthrange(int(year), int(month))[1]
    # lastDay= str(date.today().year)+"-"+str(date.today().month)+"-"+str(numDay)
    lastDay= str(year)+"-"+str(month)+"-"+str(numDay)
    # events_result = service.events().list(calendarId='primary', singleEvents=True,
                                    # orderBy = 'startTime', maxResults = 2500).execute()

    # events = events_result.get('items', [])
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



def getEventTime(availableTimes):
    '''Returns a randomly selected time slot from all of the available times slots.
    If there are no time slots, it returns an exception instead of breaking.'''

    length = len(availableTimes)
    if (length != 0):
        x = random.randrange(0, length)
        global eventSlot
        eventSlot = availableTimes[x]

        return eventSlot
    else:
        # return  '''<h1>Oops</h1>'''
        return redirect('/error')


@app.route('/reschedule', methods=['GET', 'POST'])
def rescheduleEvent():
    # print('in')
    # rescheduleNum has to start at 0, not 1!
    global rescheduleNum
    # rescheduleNum = 2

    timeSlots = dividedTimeSlots[rescheduleNum]
    e = getEventToReschedule(rescheduleNum)
    timeSlots.remove(e)

    length = len(timeSlots)
    if length != 0:
        x = random.randrange(0, length)
        eTime = timeSlots[x]
        newTime = [eTime[0], eTime[1]]
        formattedChosenOnes[rescheduleNum] = format.eventFormatDictionary(newTime, title)
        chosenTimeSlots[rescheduleNum] = newTime
    else:
        print("No available times")
        return redirect('/error')

    if rep == 1:
        return redirect('/popup')
    # elif rep > 1:
    #     return redirect('/multi_add')
    # else:
    #     print("No available times")
    #     return redirect('/error')


def getEventToReschedule(num):
    e = chosenTimeSlots[num]
    return e


def createEvent():
    '''Creates a Google Calendar event based on the randomly chosen time slot
    and prepares it to be added to the user's calendar.'''

    now = current.currentTime()
    nowDay, nowHour, nowMinute = current.getNowDHM(now)

    workStart = 480
    workEnd = 1380

    events = getCalendarEvents(now, deadLine)

    workStart = workStart + 1
    availableTimes = findTime.findAvailableTimes(nowDay, nowHour, nowMinute, workStart, workEnd, events, timeEst)


    global chosenTimeSlots
    global formattedChosenOnes
    formattedChosenOnes = []
    selectionOfTimeSlots(availableTimes)

    for i in range(len(chosenTimeSlots)):
        formattedChosenOnes.append(format.eventFormatDictionary(chosenTimeSlots[i], title))
    if rep == 1:
        return redirect('/popup')
    else:
        return redirect('/multi_add')


@app.route('/multi', methods=['GET', 'POST'])
def multiPopup():
    return render_template('multi.html')


@app.route('/multi_add', methods=['GET', 'POST'])
def multiAdd():
    global formattedChosenOnes
    global chosenTimeSlots

    reschedule = [0, 2, 3]

    for i in range(len(reschedule)):
        global rescheduleNum
        rescheduleNum = reschedule[i]
        print('before reschedule: ', chosenTimeSlots)
        print(' ')
        rescheduleEvent()
        print('after reschedule: ', chosenTimeSlots)
        print(' ')

    for i in range(len(formattedChosenOnes)):
        add = service.events().insert(calendarId = 'primary', body = formattedChosenOnes[i]).execute()
    return redirect('/form')


def divisionOfTimeSlots(availableTimes):
    global dividedTimeSlots
    dividedTimeSlots = []
    length = len(availableTimes)
    size = length // rep

    if rep == 1:
        dividedTimeSlots.append(availableTimes)
    else:
        for i in range(rep - 1):
            times = availableTimes[i * size: ((i + 1) * size)]
            dividedTimeSlots.append(times)
        dividedTimeSlots.append(availableTimes[((rep - 1) * size): length])

    return dividedTimeSlots


def selectionOfTimeSlots(availableTimes):
    global chosenTimeSlots
    chosenTimeSlots = []
    dividedTimeSlots = divisionOfTimeSlots(availableTimes)

    for i in range(rep):
        time = getEventTime(dividedTimeSlots[i])
        if time != '''<h1>Oops</h1>''':
            chosenTimeSlots.append(time)
        else:
            return render_template('/error')
    return chosenTimeSlots


@app.route('/add', methods=['GET', 'POST'])
def addEvent():
    '''Adds chosen event to the user's calendar.'''

    add = service.events().insert(calendarId = 'primary', body = formattedChosenOnes[0]).execute()
    print ('Event created: %s' % (formattedChosenOnes[0].get('summary')))
    return redirect('/form')


def getScheduledEvents():
    return formattedChosenOnes


# we need to account for:
# no time slots
# ran out of time slots
# others
@app.route('/error', methods=['GET', 'POST'])
def errorManager():
    return render_template('error.html')
