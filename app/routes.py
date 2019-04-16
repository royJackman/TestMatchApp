import operator
import random

from app import app, db
from app.forms import BugForm, DeviceForm, AddTesterForm, ConfirmForm, DevForm, EditTesterForm, getDevices, SearchForm
from app.models import Bug, Device, Experience, Tester
from datetime import datetime
from flask import flash, redirect, render_template, request, url_for

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():
    """
    Homepage that shows some testers, bugs, and devices.
    """
    # Query desired data and pass into html template
    return render_template("index.html", title="Home", bugs=random.choices(db.session.query(Bug).all(), k=10), devices=db.session.query(Device).all(), testers=db.session.query(Tester).all(), db=db, Tester=Tester, Device=Device, Bug=Bug)

@app.route('/results/<country>/<devices>', methods=['GET','POST'])
def results(country, devices):
    """
    The page that holds all search results. Multiple devices chosen using shift
    and ctrl click. Country code or ALL can be specified.

    Args:
      country: The country code specified in search parameters
      devices: An array including all device IDs in search
    Returns:
      Testers in descending order of the most experience in the given region 
      with the devices specified.
    """
    # Initialize form for searching
    form = SearchForm(country=country,device=devices)

    # Reset the country and devices variables on the fly
    country = form.country.data
    devices = form.device.data

    # Initialize the total bugs filed count and experience lists
    count = {}
    exps = {}

    # Whether or not to add an additional filter to the query
    if country == 'ALL':
        # Loop through all device_id values in the search
        for d in devices:
            # Query all the values that fit the criteria, and sort them by 
            # number of bugs
            q = db.session.query(Experience).filter_by(device_id=int(d)).all()

            # Loop through experiences, and add the new bugs to count and 
            # related experiences to exps
            for e in q:
                if e.tester_id in count.keys():
                    count[e.tester_id] += e.bugs
                    exps[e.tester_id].append(e)
                else:
                    count[e.tester_id] = e.bugs
                    exps[e.tester_id] = [e]
    else:
        # Very similar to loop above, with an extra filter for country code
        for d in devices:
            q = db.session.query(Experience).filter(Experience.tester.has(country=form.country.data)).filter_by(device_id=int(d)).all()
            for e in q:
                if e.tester_id in count.keys():
                    count[e.tester_id] += e.bugs
                    exps[e.tester_id].append(e)
                else:
                    count[e.tester_id] = e.bugs
                    exps[e.tester_id] = [e]

    # Sort the bugs count in descending order, saving the mapping
    ordering = reversed(sorted(count.items(), key=operator.itemgetter(1)))
    return render_template("results.html", title="Results", count=count, exps=exps, ordering=ordering, search=form, db=db, Tester=Tester, Device=Device)

@app.route("/bug/<id>", methods=['GET','POST'])
def bug(id):
    """
    A page to display data about bugs

    Args:
      id:   The id number of the bug
    Returns:
      Tester and device data about the bug filed
    """
    # Grab the bug in question
    bug = db.session.query(Bug).filter_by(id=id).first()

    # Check that it exists, break if not found
    if bug is None:
        flash("Bug ID Invalid")
        return redirect(url_for("index"))
    else:
        # If found, grab the tester and device info and render
        tester = db.session.query(Tester).filter_by(id=bug.tester_id).first()
        device = db.session.query(Device).filter_by(id=bug.device_id).first().device_name
        return render_template("bug.html", title="Bug Report", bug=bug, tester=tester.first_name+tester.last_name, device=device, db=db, Tester=Tester, Device=Device, Bug=Bug, Experience=Experience)

@app.route("/device/<id>", methods=['GET','POST'])
def device(id):
    """
    A page to display data about devices

    Args:
      id:   The id number of the device
    Returns:
      Device name
    """
    # Grab the device in question
    device = db.session.query(Device).filter_by(id=id).first()

    # Check for its lively existence, and render appropriate pages as needed
    if device is None:
        flash("Device ID Invalid")
        return redirect(url_for("index"))
    else:
        return render_template("device.html", title="Device Info", device=device.device_name, db=db, Tester=Tester, Device=Device, Bug=Bug, Experience=Experience)

@app.route("/tester/<id>", methods=['GET','POST'])
def tester(id):
    """
    A page to display data about Testers

    Args:
      id:   The id number of the bug
    Returns:
      All known tester data, both names, country, last known login, and devices 
      they are familiar with
    """
    tester = db.session.query(Tester).filter_by(id=id).first()
    if tester is None:
        flash("Tester ID Invalid")
        return redirect(url_for("index"))
    else:
        return render_template("tester.html", title="Tester Profile", tester=tester, db=db, Tester=Tester, Device=Device, Bug=Bug, Experience=Experience)

@app.route("/devtools", methods=['GET','POST'])
def devtools():
    """
    A hub for the developer tools. Access to add/edit/delete for all objects in 
    app.db except Experiences (They are not directly accessible)

    Redirects to:
      Add/edit/delete pages for all Bugs, Devices, and Testers
    """
    # Initialize the form to choose dev configuration
    form = DevForm()
    if form.validate_on_submit():
        # Check tool type, and redirect as appropriate, checking for ID if 
        # necessary
        tool = str(form.tool.data)
        if tool == "add":
            return redirect(url_for("add", obj=form.obj_type.data))
        elif tool == "edit":
            if form.obj_id.data is None:
                flash("Please choose a valid ID")
                return redirect(url_for("devtools"))
            return redirect(url_for("edit", obj=form.obj_type.data, id=int(form.obj_id.data)))
        elif tool == "delete":
            if form.obj_id.data is None:
                flash("Please choose a valid ID")
                return redirect(url_for("devtools"))
            return redirect(url_for("delete", obj=form.obj_type.data, id=int(form.obj_id.data)))
        else:
            flash("Unrecognized Tool")
            return redirect(url_for("devtools"))
    return render_template("devtools.html", title="Devtools", form=form)

@app.route("/add/<obj>", methods=['GET','POST'])
def add(obj):
    """
    General page for adding items

    Args:
      obj:  The type of the object to be added
    Returns:
      Confirmation of object addition
    """
    if obj == "Bug":
        # Initialize form that holds bug data
        form = BugForm()
        if form.validate_on_submit():
            # Create an instance of the bug
            bug = Bug(device_id=int(form.device_id.data), tester_id=int(form.tester_id.data))

            # Add to the database
            db.session.add(bug)

            # Check if the experience for this device/tester combo exists
            exp = db.session.query(Experience).filter_by(device_id=int(form.device_id.data)).filter(Experience.tester.id == int(form.tester_id.data)).first()

            # If it's new, make an instance of it, and append it to the 
            # relevanet tester
            if exp is None:
                exp = Experience(device_id = int(form.device_id.data), bugs=1)
                db.session.query(Tester).filter_by(id=int(form.tester_id.data)).first().experience.append(exp)
            else:
                # If it's not, increment the number of bugs found for that 
                # experience
                exp.bugs += 1
            # Commit all changes 
            db.session.commit()

            # Confirm addition and render
            flash(obj + " added successfully")
            return redirect(url_for("devtools"))
        return render_template("add.html", title="Add Bug", form=form)
    elif obj == "Device":
        # Initialize device data form
        form = DeviceForm()
        if form.validate_on_submit():
            # Create a device instance and add it to the database
            device = Device(device_name=form.device_name.data)
            db.session.add(device)

            # Commit, confirm, and redirect
            db.session.commit()
            flash(obj + " added successfully")
            return redirect(url_for("devtools"))
        return render_template("add.html", title="Add Device", form=form)
    elif obj == "Tester":
        # Init the form, etc. etc.
        form = AddTesterForm()
        if form.validate_on_submit():
            # Create the tester instance
            tester = Tester(first_name=form.first_name.data, last_name=form.last_name.data, country=form.country.data, last_login=datetime.strptime(form.last_login.data, '%Y-%m-%d %H:%M:%S'))

            # Add all devices to the devices relationship 
            for i in form.devices.data.split(" "):
                device = db.session.query(Device).filter_by(id=int(i)).first()
                tester.devices.append(device)

            # Add, commit, confirm, redirect
            db.session.add(tester)
            db.session.commit()
            flash(obj + " added successfully")
            return redirect(url_for("devtools"))
        return render_template("add.html", title="Add Tester", form=form)
    else:
        # Object type error handling
        flash("Object type not recognized")
        return redirect(url_for("devtools"))

@app.route("/edit/<obj>/<id>", methods=['GET','POST'])
def edit(obj, id):
    """
    General page for editing items

    Args:
      obj:  The type of the object to be edited
      id:   ID of object being edited
    Returns:
      Confirmation of object edit
    """
    # Check the object type
    if obj == "Bug":
        # Grab the bug from the database, and init the form with the bug's data 
        # as default input
        bug = db.session.query(Bug).filter_by(id=id).first()
        form = BugForm(device_id=bug.device_id, tester_id=bug.tester_id)
        if form.validate_on_submit():
            # Checking that parameters have been changed
            if bug.device_id == int(form.device_id.data) and bug.tester_id == int(form.tester_id.data):
                flash("Please change some parameters")
                return redirect(url_for("edit", obj="Bug", id=id))
            # Decrement the bug from the experience it was originally part of
            exp = db.session.query(Experience).filter_by(device_id=int(bug.device_id)).filter(Experience.tester.id == bug.tester_id).first()
            exp.bugs -= 1

            # Then increment the bug count of the experience it is now part of
            exp = db.session.query(Experience).filter_by(device_id=int(form.device_id.data)).filter(Experience.tester.id == int(form.tester_id.data)).first()
            if exp is None:
                exp = Experience(device_id = int(form.device_id.data), bugs=1)
                db.session.query(Tester).filter_by(id=int(form.tester_id.data)).first().experience.append(exp)
            else:
                exp.bugs += 1

            # Make changes, commit, and redirect
            bug.device_id = int(form.device_id.data)
            bug.tester_id = int(form.tester_id.data)
            db.session.commit()
            flash(obj + " edited successfully")
            return redirect(url_for("devtools"))
        return render_template("edit.html", title="Edit Bug", form=form)
    elif obj == "Device":
        # Get the desired device from memory
        device = db.session.query(Device).filter_by(id=id).first()

        # Device does not exist error handling
        if device is None:
            flash("No " + obj + " with ID " + str(id))
            return redirect(url_for("devtools"))
        
        # Init form with device default
        form = DeviceForm(device_name=device.device_name)
        if form.validate_on_submit():
            # Change, commit, confirm, redirect
            device.device_name = form.device_name.data
            db.session.commit()
            flash(obj + " edited successfully")
            return redirect(url_for("devtools"))
        return render_template("edit.html", title="Edit Device", form=form)
    elif obj == "Tester":
        # Grab the tester and init the form with his.her defaults
        tester = db.session.query(Tester).filter_by(id=id).first()
        form = EditTesterForm(first_name=tester.first_name, last_name=tester.last_name, country=tester.country, devices=" ".join([str(d.id) for d in tester.devices]))
        if form.validate_on_submit():
            # Change data, reset devices, commit, confirm, redirect
            tester.first_name = form.first_name.data
            tester.last_name = form.last_name.data
            tester.country = form.country.data
            for i in form.devices.data.split(" "):
                device = db.session.query(Device).filter_by(id=int(i)).first()
                if device not in tester.devices:
                    tester.devices.append(device)

            db.session.commit()
            flash(obj + " edited successfully")
            return redirect(url_for("devtools"))
        return render_template("edit.html", title="Edit Tester", form=form)
    else:
        # Type unkown error handler
        flash("Object type not recognized")
        return redirect(url_for("devtools"))

@app.route("/delete/<obj>/<id>", methods=['GET','POST'])
def delete(obj, id):
    """
    Object deletion confirmation page

    Args:
      obj:  The type of the object to be deleted
      id:   ID of object being deleted
    Returns:
      Confirmation of object deletion
    """
    # Initialize Confirmation form
    form = ConfirmForm()
    if form.validate_on_submit():
        # Check user is sure
        if form.areYouSure.data:
            # If so, delete, commit, confirm, redirect
            if obj == "Bug":
                db.session.delete(db.session.query(Bug).filter_by(id=id).first())
            elif obj == "Device":
                db.session.delete(db.session.query(Device).filter_by(id=id).first())
            elif obj == "Tester":
                db.session.delete(db.session.query(Tester).filter_by(id=id).first())
            else:
                flash("Object type not recognized")
                return redirect(url_for("devtools"))
            db.session.commit()
        else:
            return redirect(url_for("devtools"))
    return render_template("delete.html", title="Delete " + obj, form=form)