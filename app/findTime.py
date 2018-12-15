#findTime.py
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

# Finds open time slots for events.
class FindTime:
    def __init__(self, service, dueDate, current):
        self.service = service
        self.dueDate = dueDate
        self.current = current
        pass

    def findAvailableTimes(self, nowDay, nowHour, nowMinute, workStart, workEnd, events, timeEst):
        '''Calculates every available time slot in relation to the events on the user's
        calender from now until the assignment due date. Returns a list of these time slots.'''

        global format
        format = Format()
        global timeSlot
        timeSlot = TimeSlot(timeEst)
        global availableTimes
        availableTimes = []

        try:
            for i in range(len(events) - 1):

                event1 = events[i]
                event2 = events[i + 1]
                e1, e2 = format.formatEvent(event1, event2)
                self.compareEvents(e1, e2, workStart, workEnd, nowDay, nowHour, nowMinute, timeEst)

            lastEvent = events[len(events) - 1]
            secondToLast = events[len(events) - 2]
            self.compareLastEvent(lastEvent, secondToLast, workStart, workEnd, nowDay, nowHour, nowMinute, timeEst)

            self.checkEmptyDays(workStart, workEnd, timeEst)

            availableTimes.sort()
            return availableTimes
        except:
            global msg
            msg = "There isn't enough time. Try again"
            return redirect('/error')


    def checkEmptyDays(self, workStart, workEnd, timeEst):
        global deadline
        deadline = datetime.datetime(int(self.dueDate[0:4]), int(self.dueDate[5:7]), int(self.dueDate[8:10]))
        global now
        now = datetime.datetime(int(self.current[0:4]), int(self.current[5:7]), int(self.current[8:10]))

        global startMinutes
        global startHours
        startMinutes = workStart % 60
        startHours = (workStart - startMinutes) / 60

        endMinutes = workEnd % 60
        endHours = (workEnd - endMinutes) / 60

        global enoughTimeEmpty
        enoughTimeEmpty = (workEnd - workStart) >= (timeEst * 60) + 30

        if now.month == deadline.month and now.year == deadline.year:
            num = deadline.day - now.day
            self.setUpEmpty(now, num)

        elif (deadline.month - now.month == 1) or (now.month == 12 and deadline.month == 1):
            self.monthRangeBeginEnd()

        elif (deadline.month - now.month > 1) and (now.year == deadline.year):
            self.monthRangeBeginEnd()
            for i in range(deadline.month - now.month - 1):
                month = now.month + i + 1
                weekday, monthDays = calendar.monthrange(now.year, month)

                start = datetime.datetime(now.year, month, 1)
                self.setUpEmpty(start, monthDays)

                monthEnd = datetime.datetime(now.year, month, monthDays)
                nextMonthStart = datetime.datetime(now.year, month + 1, 1)
                self.lastDayOfMonth(monthEnd, nextMonthStart, monthDays)

        elif (now.month - deadline.month < 11) and (now.year != deadline.year):
            self.monthRangeBeginEnd()
            if now.month != 12:
                for i in range(12 - now.month):
                    month = now.month + i + 1
                    weekday, monthDays = calendar.monthrange(now.year, month)

                    start = datetime.datetime(now.year, month, 1)
                    self.setUpEmpty(start, monthDays)

                    monthEnd = datetime.dateTime(now.year, month, monthDays)
                    if month == 12:
                        nextMonthStart = datetime.dateTime(now.year + 1, 1, 1)
                    else:
                        nextMonthStart = datetime.datetime(now.year, month + 1, )
                    self.lastDayOfMonth(monthEnd, nextMonthStart, monthDays)

            if deadline.month != 1:
                for i in range(deadline.month - 1):
                    month = 1 + i
                    weekday, monthDays = calendar.monthrange(deadline.year, month)

                    start = datetime.datetime(deadline.year, month, 1)
                    self.setUpEmpty(start, monthDays)


    def monthRangeBeginEnd(self):
        weekday, monthDays = calendar.monthrange(now.year, now.month)
        num = monthDays - now.day
        self.setUpEmpty(now, num)
        self.lastDayOfMonth(now.month, now.year)
        dt = datetime.datetime(deadline.year, deadline.month, 1)
        self.setUpEmpty(dt, deadline.day - 1)


    def lastDayOfMonth(self, month, year):
        weekday, monthDays = calendar.monthrange(year, month)
        min = format.formatDT2(year, month, monthDays, 0, 0, 0)
        minDT = datetime.datetime(year, month, monthDays)
        if month == 12:
            nextMonth = 1
            year += 1
        else:
            nextMonth = month + 1
        max = format.formatDT2(year, nextMonth, 1, 0, 0, 0)
        lastDay = self.service.events().list(calendarId='primary', timeMin = min,
                                        timeMax = max, singleEvents=True,
                                        orderBy = 'startTime').execute().get('items', [])
        self.compareEmpty(minDT, lastDay)


    def setUpEmpty(self, dt, num):
        for i in range(num):
            minDay = dt.day + i
            weekday, monthDays = calendar.monthrange(dt.year, dt.month)
            if minDay == monthDays:
                maxDay = 1
                maxMonth = dt.month + 1
            else:
                maxDay = minDay + 1
                maxMonth = dt.month
            timeMinDT = datetime.datetime(dt.year, dt.month, minDay)
            timeMin = format.formatDT2(dt.year, dt.month, minDay, 0, 0, 0)
            timeMax = format.formatDT2(dt.year, maxMonth, maxDay, 0, 0, 0)

            events = self.service.events().list(calendarId='primary', timeMin = timeMin,
                                            timeMax = timeMax, singleEvents=True,
                                            orderBy = 'startTime').execute().get('items', [])
            self.compareEmpty(timeMinDT, events)


    def compareEmpty(self, dt, events):
        if len(events) == 0:
            morning = datetime.datetime(dt.year, dt.month, dt.day, int(startHours), int(startMinutes)) - datetime.timedelta(minutes = 15)
            time = timeSlot.afterTimeSlot(morning)
            availableTimes.append(time)


    def compareLastEvent(self, lastEvent, secondToLast, workStart, workEnd, nowDay, nowHour, nowMinute, timeEst):
        '''Accounts for finding the time slots around the the last event before the
        deadline. Also accounts for if there is only one event before the deadline.'''

        estTimeMin = timeEst * 60
        estMins = estTimeMin % 60
        estHours = (estTimeMin - estMins) / 60
        openTime = self.openTimeWindow(workStart, workEnd)

        lastEnd, lastStart = format.formatEvent(lastEvent, lastEvent)
        secondEnd, secondStart = format.formatEvent(secondToLast, secondToLast)

        timeWindow = (lastEnd.hour * 60) + lastEnd.minute + (estTimeMin + 30)

        beforeTime = (lastStart.hour * 60 + lastStart.minute) - (workStart)
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

        if(((lastEnd.hour*60) in openTime) and (timeWindow in openTime)):
            time = timeSlot.afterTimeSlot(lastEnd)
            availableTimes.append(time)


    def compareEvents(self, e1, e2, workStart, workEnd, nowDay, nowHour, nowMinute, timeEst):
        '''Compares each pair of events on the user's calendar from now until the
        entered deadline. If there is enough time between the events, the time slot
        between them is added to the list of available times.'''

        estTimeMin = timeEst * 60
        estMins = estTimeMin % 60
        estHours = (estTimeMin - estMins) / 60
        openTime = self.openTimeWindow(workStart, workEnd)

        sameDay = (e1.day == e2.day)

        #for time in morning before eventTime
        morningTime = (e2.hour * 60 + e2.minute) - (workStart)
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

        if(now and (sameDay and enoughTime and ((e1.hour*60) in openTime) and (timeWindow in openTime))):
            time = timeSlot.afterTimeSlot(e1)
            availableTimes.append(time)

        if(now and (not sameDay and enoughTime2 and ((e1.hour*60) in openTime) and (timeWindow in openTime))):
            time = timeSlot.afterTimeSlot(e1)
            availableTimes.append(time)

        if(not sameDay and enoughMorningTime):
            time = timeSlot.beforeTimeSlot(e2)
            availableTimes.append(time)


    def openTimeWindow(self, openStartTime, openEndTime):
        '''Returns the time during the day when the user can work on assignments
        in terms of hours and in terms of the minutes out of the entire minutes
        in a day.'''

        openTime = range(openStartTime, openEndTime)
        return openTime
