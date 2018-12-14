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

def loginCheck():
    try:
        if service == None:
            return redirect('/')
        else:
            return 0
    except:
        return 1

@app.route('/', methods=['GET','POST'])
def main():

    global workStart
    global workEnd
    checkForm2.has_been_called = False

    global current
    current = Time()

    global format
    format = Format()

    global service

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
    # try:
    #     print (service)
    x = loginCheck()
    if x == 1:
        return redirect('/')
    if request.method == 'POST': #this block is only entered when the form is submitted
        if not request.headers.get('X-Requested-With'):

            global title
            title = request.form.get('Title')

            global timeEst
            timeEst = float(request.form.get('est'))

            global deadline
            deadline = request.form.get('dead')

            global rep
            rep = int(request.form.get('rep'))

            return createEvent()
        else:
            print ("else case")

    return render_template('index.html')
    # except:
    #     return redirect('/')


@app.route('/form2', methods=['GET', 'POST'])
def form2():
    # try:
    #     print (service)
    x = loginCheck()
    if x == 1:
        return redirect('/')
    if request.method == 'POST': #this block is only entered when the form is submitted

        if not request.headers.get('X-Requested-With'):

            global earliestWorkTime
            earliestWorkTime = request.form.get('earliest')

            global latestWorkTime
            latestWorkTime = request.form.get('latest')
            checkForm2()

        else:
            print("else statement")

    return render_template('index.html')
    # except:
    #     return redirect('/')


def checkForm2():
    checkForm2.has_been_called = True
    pass


@app.route('/popup', methods=['GET', 'POST'])
def popup():
    print("in popup")

    # global formattedChosenOnes

    x = loginCheck()
    if x == 1:
        return redirect('/')

    try:
        displayFormat()
        title = formattedChosenOnes[0]
        print (title["start"].get("dateTime"))

        if len(dividedTimeSlots[0]) != 1:
            return render_template('popup.html', event=displayList[0], title = title)
        else:
            print (len(dividedTimeSlots[0]))
            options = "There are no further time slots available"
            return render_template('popup.html', event=displayList[0], title = title, options=options)
    except:
        return redirect("/error")

@app.route('/allEvents', methods=['GET', 'POST'])
def getEvents():

    x = loginCheck()
    if x == 1:
        return redirect('/')

    from datetime import date
    year = request.args.get('year')
    month = request.args.get('month')
    firstDay = str(year)+"-"+str(month)+"-01"
    numDay = calendar.monthrange(int(year), int(month))[1]
    lastDay= str(year)+"-"+str(month)+"-"+str(numDay)

    events = getCalendarEvents(firstDay + 'T00:00:00-06:00', lastDay) #replace deadline with something else
    eventsJSON = jsonify(events)
    eventsJSON.status_code = 200
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
        eventSlot = availableTimes[x]
        return eventSlot
    else:
        global msg
        msg = "No Time available"
        print("No Time available")
        return redirect('/error')


def reassignSlot(start, end):
    global eventSlot
    eventSlot = [start,end]
    return eventSlot


@app.route('/reschedule', methods=['GET', 'POST'])
def rescheduleEvent():

    x = loginCheck()
    if x == 1:
        return redirect('/')

    global msg
    global formattedChosenOnes
    global chosenTimeSlots
    global rescheduleNum
    test = 0
    rescheduleVal = []

    for i in range(5):
        if request.args.get(str(i)) == "true":
            rescheduleVal.append(int(i))
            test = 253

    if test == 0:
        print (test)
        rescheduleVal.append(0)

    for i in range(len(rescheduleVal)):
        rescheduleNum = rescheduleVal[i]
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
            msg = "No available times anymore"
            print("No available times anymore")
            return redirect('/error')

    if rep == 1:
        return redirect('/popup')
    # elif rep > 1:
    #     return redirect('/multi_add')
    else:
        msg = "No available times"
        print("No available times")
        return redirect('/multi')


def getEventToReschedule(num):
    e = chosenTimeSlots[num]
    return e


def createEvent():
    global rep
    '''Creates a Google Calendar event based on the randomly chosen time slot
    and prepares it to be added to the user's calendar.'''
    print('in create event')

    now = current.currentTime()
    nowDay, nowHour, nowMinute = current.getNowDHM(now)
    nowYear, nowMonth = current.getNowYM(now)

    global workStart
    global workEnd
    global findTime
    findTime = FindTime(service, deadline, now)

    if checkForm2.has_been_called:
        workStart = int(earliestWorkTime[:2])*60 + int(earliestWorkTime[3:])
        workEnd = int(latestWorkTime[:2])*60 + int(latestWorkTime[3:])

    else:
        workStart = 480
        workEnd = 1380

    if not current.isDST(datetime.datetime(nowYear, nowMonth, nowDay)):
        workStart += 60
        workEnd += 60

    events = getCalendarEvents(now, deadline)

    availableTimes = findTime.findAvailableTimes(nowDay, nowHour, nowMinute, workStart, workEnd, events, timeEst)

    global chosenTimeSlots
    global formattedChosenOnes
    formattedChosenOnes = []
    try:
        selectionOfTimeSlots(availableTimes)
        for i in range(len(chosenTimeSlots)):
            formattedChosenOnes.append(format.eventFormatDictionary(chosenTimeSlots[i], title))
    except:
        global msg
        msg = "This is not physically possible. Come back when you have more time, need less time, or have control over the universe. Then we'll talk."
        print ("so, something went wrong")
        return redirect('/error')
    if rep == 1:
        return redirect('/popup')
    else:
        return redirect('/multi')


@app.route('/multi', methods=['GET', 'POST'])
def multiPopup():

    x = loginCheck()
    if x == 1:
        return redirect('/')
    warning = []
    displayFormat()
    localChosenTimes = ""
    for i in range(len(displayList)):
        localChosenTimes = localChosenTimes + " AND " + displayList[i]
        print (localChosenTimes)
    # warning = []
    for i in range(rep):
        if len(dividedTimeSlots[i]) == 1:
            print (len(dividedTimeSlots[i]))
            warning.insert(i, "There are no further times available")
    return render_template('multi.html', displayList=displayList, localChosenTimes=localChosenTimes, formattedChosenOnes = formattedChosenOnes, rep=rep, warning=warning)


@app.route('/multi_add', methods=['GET', 'POST'])
def multiAdd():

    x = loginCheck()
    if x == 1:
        return redirect('/')

    global formattedChosenOnes
    for i in range(len(formattedChosenOnes)):
        add = service.events().insert(calendarId = 'primary', body = formattedChosenOnes[i]).execute()
    return redirect('/form')


@app.route('/multi_res', methods=['GET', 'POST'])
def multiRes():

    x = loginCheck()
    if x == 1:
        return redirect('/')

    return render_template('multiRes.html', rep=rep)


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
            print ("error = oops")
            return render_template('/error')
    return chosenTimeSlots


@app.route('/add', methods=['GET', 'POST'])
def addEvent():
    '''Adds chosen event to the user's calendar.'''

    x = loginCheck()
    if x == 1:
        return redirect('/')

    add = service.events().insert(calendarId = 'primary', body = formattedChosenOnes[0]).execute()
    print ('Event created: %s' % (formattedChosenOnes[0].get('summary')))
    return redirect('/form')


def displayFormat():
    global displayList
    displayList = []
    fmt = '%A, %B %d, from %I:%M%p'
    fmt2 = '%I:%M%p'

    for i in range(len(formattedChosenOnes)):
        chosenStart = formattedChosenOnes[i]["start"].get("dateTime")
        chosenEnd = formattedChosenOnes[i]["end"].get("dateTime")

        chosenStart = chosenStart[:22] + chosenStart[23:]
        chosenEnd = chosenEnd[:22] + chosenEnd[23:]
        startObj = datetime.datetime.strptime(chosenStart, "%Y-%m-%dT%H:%M:%S%z")
        endObj = datetime.datetime.strptime(chosenEnd, "%Y-%m-%dT%H:%M:%S%z")

        if not current.isDST(startObj):
            startObj -= datetime.timedelta(hours = 1)
            endObj -= datetime.timedelta(hours = 1)

        stringDate = startObj.strftime(fmt) + ' to ' + endObj.strftime(fmt2)
        displayList.append(stringDate)
    return displayList


def getScheduledEvent():
    return event


# we need to account for:
# no time slots
# ran out of time slots
# others
@app.route('/error', methods=['GET', 'POST'])
def errorManager():
    x = loginCheck()
    if x == 1:
        return redirect('/')

    return render_template('error.html', msg=msg)

@app.route('/end', methods=['GET', 'POST'])
def signOut():
    global service
    service = None
    return redirect('/')
