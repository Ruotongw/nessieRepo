# nessieRepo
This web-app is built using Flask. Please install/update-
  Python 3:                                 https://www.python.org/
  Pip:                                      https://pypi.org/project/Flask/1.0.2/
  Flask:                                    https://pypi.org/project/Flask/1.0.2/

Then navigate to the project folder and-
  Setup Venv:   http://flask.pocoo.org/docs/1.0/installation/#virtual-environments
  Activate Venv:
    Windows:    venv\Scripts\activate
    Unix/Mac:   . venv/bin/activate
  Run: python -m pip install --upgrade pip

  Setup Flask:  http://flask.pocoo.org/docs/1.0/installation/#virtual-environments
    pip install Flask

  Install Pip based dependencies: (pip install ____)
    --upgrade google-api-python-client oauth2client
    Pytz
    tzlocal
    Pandas

  set the flask app:
    Windows:    set FLASK_APP=run.py
    Unix/Mac:   export FLASK_APP=run.py

  use the command ( flask run ) to start the server
  use any browser to access http://localhost:5000
