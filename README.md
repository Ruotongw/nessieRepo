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

  Install Pytz:
    Windows:    python setup.py install
    Unix/Mac:   python setup.py install
    If this doesn't work, try the other options at: https://pypi.org/project/pytz/

  Install Pip based dependencies: (pip install ____)
    Flask
    --upgrade google-api-python-client oauth2client
    tzlocal
    Pandas

  set the flask app:
    Windows:    set FLASK_APP=run.py
    Unix/Mac:   export FLASK_APP=run.py

  use the command ( flask run ) to start the server
  use any browser to access http://localhost:5000
