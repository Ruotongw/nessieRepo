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

@app.route('/', methods=['GET','POST'])
def main():

    global service

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
            print (service)
            # Get profile info from ID token
            # userid = credentials.id_token['sub']
            # email = credentials.id_token['email']
            # form(credentials)
            now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

            print ('phase 1')
            return form()
            # redirect(url_for('form'))
            # return form(credentials)

    return '''<html itemscope itemtype="http://schema.org/Article">
                  <head>
                    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js">
                    </script>
                    <script src="https://apis.google.com/js/client:platform.js?onload=start" async defer>
                    </script>
                    <script>
                    function start() {
                      gapi.load('auth2', function() {
                        auth2 = gapi.auth2.init({
                          client_id: '333626695075-ldu172t8tcfaek30cv9ln66h6jpp0khj.apps.googleusercontent.com',
                          // Scopes to request in addition to 'profile' and 'email'
                          scope: 'https://www.googleapis.com/auth/calendar'
                        });
                      });
                    }
                    </script>
                  </head>
                  <body>

                        <input id=Title type="text" name="Title"><br>
                        <input id=est type="number" min="0" name="est"><br>
                        <input id=dead type="date" name="dead"><br>
                        <button id="signinButton">Sign in with Google</button>
                        <script>
                          $('#signinButton').click(function() {
                            console.log("test")
                            // signInCallback defined in step 6.
                            console.log("got to line 25");
                            auth2.grantOfflineAccess().then(signInCallback);
                          });
                          </script>
                          <script>
                          function signInCallback(authResult) {
                          console.log("got to line 35");
                            console.log("got to line 37");
                            console.log(authResult['code']);
                            if (authResult['code']) {
                              console.log("got to line 39");

                              // Hide the sign-in button now that the user is authorized, for example:
                              $('#signinButton').attr('style', 'display: none');

                              // Send the code to the server
                              $.ajax({
                                type: 'POST',
                                url: '/',
                                // Always include an `X-Requested-With` header in every AJAX request,
                                // to protect against CSRF attacks.
                                headers: {
                                  'X-Requested-With': 'XMLHttpRequest'
                                },
                                contentType: 'application/octet-stream; charset=utf-8',
                                success: function(result) {
                                  console.log("the authentication was a success");
                                },
                                processData: false,
                                data: authResult['code']
                              });
                            } else {
                              // There was an error.
                            }
                          }
                        </script>

                  </body>
                </html>'''

@app.route('/', methods=['GET', 'POST']) #allow both GET and POST requests
def form():
    print (service)
    # redirect("/form")
    # # render_template('index.html')
    # if request.method == 'POST': #this block is only entered when the form is submitted
    #     # if not request.headers.get('X-Requested-With'):
    #
    #     title = request.Title
    #     print (title)
    #     timeEst = request.est
    #     print (title)
    #
    #     DedLine = request.dead
    #     print (DedLine)
    #
    #     print ('phase 1')
    #     # setUp()
    #     createEvent(title, timeEst, DedLine, credentials)
        # else:
        #     print ("else case")
            # render_template('newIndex.html')
    return       '''<form method="POST">
                       Assignment Title: <input type="text" name="Title"><br>
                       Estimated Time: <input type="number" min="0" name="est"><br>
                       Deadline: <input type="date" name="dead"><br>
                       <input type="submit" value="Create"><br>
                   </form>'''
