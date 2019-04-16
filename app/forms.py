from app import app, db
from app.models import Bug, Device, Experience, Tester
from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, FloatField, SelectField, SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError

def getDevices():
    # Return device id/name pairings to populate the search form
    return [(d.id, d.device_name) for d in db.session.query(Device).all()]

class BugForm(FlaskForm):
    device_id = IntegerField("Device ID", validators=[DataRequired()])
    tester_id = IntegerField("Tester ID", validators=[DataRequired()])
    submit = SubmitField("Submit")

class DeviceForm(FlaskForm):
    device_name = StringField("Device Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

class AddTesterForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    country = StringField("Country", validators=[DataRequired()])
    last_login = StringField("Last Login Time", validators=[DataRequired()])
    devices = StringField("Device IDs, separated by spaces", validators=[DataRequired()])
    submit = SubmitField("Submit")

class ConfirmForm(FlaskForm):
    areYouSure = BooleanField("Are you sure?", validators=[DataRequired()])
    submit = SubmitField("Submit")

class DevForm(FlaskForm):
    tool = SelectField('Which tool would you like?', choices=[("add", "Add"), ("edit", "Edit"), ("delete", "Delete")], default="add", validators=[DataRequired()])
    obj_type = SelectField("Object type desired", choices=[("Bug", "Bug"), ("Device", "Device"), ("Tester", "Tester")], default="Device", validators=[DataRequired()])
    obj_id = IntegerField("Object ID for editing or deleting")
    submit = SubmitField("Let's go!")

class EditTesterForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    country = StringField("Country", validators=[DataRequired()])
    devices = StringField("Device IDs, separated by spaces", validators=[DataRequired()])
    submit = SubmitField("Submit")

class SearchForm(FlaskForm):
    country = StringField("Country code or ALL", validators=[DataRequired()])
    device = SelectMultipleField("Device(s)", choices=getDevices(), validators=[DataRequired()])
    submit = SubmitField("Submit")