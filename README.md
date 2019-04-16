# TesterMatch

In this Github repo is the testermatch app, which is used for sorting through testers to find those with the most experience using certain devices. 

## Setup

First, please run 

`pip install flask flask_migrate flask_sqlalchemy flask_wtf wtforms`

which should download all the required libraries to run this app.

## Running a local instance of the app

After doanloading the necessary libraries, please navigate to the testerMatching folder. Once there, run the command 

`export FLASK_APP=testermatching.py` if on Unix machines, or

`set FLASK_APP=testermatching.py` on windows machines.

This will set your flask app to testermatcher. Finally, to start up the server, run

`flask run`

## Accessing the app

The default location for the server to start running is `http://127.0.0.1:5000/`. 

## Website navigation

The basic architecture of the app is to show a sampling of the testers, bugs, and devices on the home page, have a seperate search page, where one can choose whichever combination of countries and devices they choose to find the most experienced developer with those criteria. Finally, There are devtools for adding, editing, and deleting existing data.