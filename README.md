# nessieRepo
This web-app is built using Flask. Please install-
  The latest version of Python:             https://www.python.org/
  Flask:                                    https://pypi.org/project/Flask/1.0.2/

Then navigate to the project folder and-
  Setup Venv:   http://flask.pocoo.org/docs/1.0/installation/#virtual-environments
  Activate Venv:
    Windows:    . venv/bin/activate
    Unix/Mac:   . venv/bin/activate

  Install Pytz (only need to do this once):
    Windows:    python setup.py install
    Unix/Mac:   python setup.py install
    If this doesn't work, try the other options at: https://pypi.org/project/pytz/

  Install Pandas (only need to do this once):
    Windows:    pip install pandas
    Unix/Mac:   pip install pandas

  set the flask app:
    Windows:    set FLASK_APP=run.py
    Unix/Mac:   export FLASK_APP=run.py

  use the command ( flask run ) to start the server
  use any browser to access http://localhost:5000
