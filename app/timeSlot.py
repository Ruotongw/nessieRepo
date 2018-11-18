#timeSlot.py
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

class TimeSlot:

    def __init__(self, estimate):
        self.estimate = estimate
        global format
        format = Format()


    def beforeTimeSlot(self, event2):
        '''Returns the time slot before event2. Used for the first event of the day,
        given that there is enough time between that event and the start of working
        hours.'''

        print('entered before')

        localizedTime = self.estimate

        event2Min = (event2.hour * 60) + event2.minute
        localizedTime = localizedTime * 60

        startTime = event2Min - localizedTime - 15
        startMin = startTime % 60
        startHour = (startTime - startMin) / 60

        endTime = event2Min -15
        endMin = endTime % 60
        endHour = (endTime - endMin)/60

        eventStart = format.formatDT2(event2.year, event2.month, event2.day, startHour, startMin, event2.second)
        eventEnd = format.formatDT2(event2.year, event2.month, event2.day, endHour, endMin, event2.second)

        timeSlot = [eventStart, eventEnd]
        return timeSlot


    def afterTimeSlot(self, event1):
        '''Returns the time slot after event1. Used for most scheduling cases, hence
        the name generalTimeSlot.'''

        print('entered after')
        localizedTime = self.estimate
        print("localized", localizedTime)

        event1Min = (event1.hour * 60) + event1.minute
        localizedTime = localizedTime * 60

        startTime = event1Min + 15
        startMin = startTime % 60
        startHour = (startTime - startMin) / 60

        endTime = startTime + localizedTime
        endMin = endTime % 60
        endHour = (endTime - endMin)/60

        print("before format")

        eventStart = format.formatDT2(event1.year, event1.month, event1.day, startHour, startMin, event1.second)
        eventEnd = format.formatDT2(event1.year, event1.month, event1.day, endHour, endMin, event1.second)

        print("after format")
        timeSlot = [eventStart, eventEnd]
        print("timeSlot", timeSlot)
        return timeSlot
