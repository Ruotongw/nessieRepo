#formats.py
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

class Format:

    def __init__(self):
        pass


    def formatEvent(self, event1, event2):
        '''Returns event1 and event2 in the correct datetime format to use in
        findAvailableTimes(). This requires turning the start and end time strings
        into dateTime objects, converting them to UTC time, and normalizing them to
        account for daylight savings time.'''

        print("has entered")
        fmt = '%Y-%m-%dT%H:%M:%S%z'

        e1str = event1['end'].get('dateTime')
        e2str = event2['start'].get('dateTime')

        e1str = e1str[:22] + e1str[23:]
        e2str = e2str[:22] + e2str[23:]

        print("About to use dateTime")
        e1 = datetime.datetime.strptime(e1str, fmt)
        e2 = datetime.datetime.strptime(e2str, fmt)

        utc = timezone('UTC')
        chi = timezone('America/Chicago')

        e1 = e1.astimezone(utc)
        e2 = e2.astimezone(utc)

        print("String formatting")
        e1.strftime(fmt)
        e2.strftime(fmt)

        print("After strings, before daylight")
        print(e1, e2)
        e1, e2 = self.inDaylightSavings(e1, e2)
        print("Used daylight savings")

        e1.strftime(fmt)
        e2.strftime(fmt)

        e1 = chi.normalize(e1)
        e2 = chi.normalize(e2)
        print("E1,E2", e1, e2)

        return e1, e2

    def formatDT1(self, dt):
        '''Returns a datetime string of the given datetime object formatted
        correctly for the Google API.'''

        fmt = '%Y-%m-%dT%H:%M:%S%z'
        dt = dt.strftime(fmt)
        dt = dt[:22] + ':' + e2[22:]

        return dt


    def formatDT2(self, year, month, day, hour, minute, second):
        '''Returns a datetime string with the given integers formatted correctly
        for the Google API.'''

        print("entered format")
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
        print("dt", dt)

        return dt

    def inDaylightSavings(self, e1, e2):
        '''Checks whether event1 and e2 are in daylight savings time and adds an
        hour accordingly.'''

        print("entered daylgiht savings")
        DSTMonths = [4, 5, 6, 7, 8, 9, 10]

        if (e1.month == 11 and e1.day < 4) or e1.month in DSTMonths:
            e1 = e1 + datetime.timedelta(hours = 0)
            e2 = e2 + datetime.timedelta(hours = 0)
        else:
            e1 = e1 + datetime.timedelta(hours = 1)
            e2 = e2 + datetime.timedelta(hours = 1)

        print("e1,e2", e1, e2)
        return e1, e2
