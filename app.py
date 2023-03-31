import os
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, jsonify, session
from flask_mail import Mail, Message
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from datetime import datetime

from helpers import error, login_required, NGN

# Configure application
app = Flask(__name__)

#Configure uploads
app.config["UPLOAD_FOLDER"] = "static/assets/farms"
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024 #2MB
app.config["ALLOWED_EXTENSIONS"] = [".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico"]


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["NGN"] = NGN

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.config["SESSION_COOKIE_NAME"] = "session"

app.config["MAIL_DEFAULT_SENDER"] = "FARMFUND"
app.config["MAIL_PASSWORD"] = "imldmcuxsdmqhktq"
app.config["MAIL_PORT"] = 465
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USERNAME"] = "farmfundp@gmail.com"
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///farms.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# The Home Route
@app.route("/")
@login_required
def index():
    """Give an introduction of activities"""
    # Remember user
    user_id = session["user_id"]

    # Query database for user details
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)

    # Query database for farm records
    farms = db.execute("SELECT * FROM farm ORDER BY date LIMIT 6")

    # Render the index.html
    return render_template("index.html", username=user[0]["username"], farms=farms, NGN=NGN)


# The projects route
@app.route("/projects")
@login_required
def projects():
    """Show farmers portfolio"""

    # Query database for farm table data
    farm = db.execute("SELECT * FROM farm GROUP BY farm_name")

    # Render the projects html
    return render_template("projects.html", farm=farm, NGN=NGN)


# The dashboard route
@app.route("/dashboard")
@login_required
def dashboard():
    """Show User's Dashboard"""
    # Remember user
    user_id = session["user_id"]

    # Remember user track
    user_track = session["track"]

    # Check if user is a farmer
    if user_track == "Farmer":
        # Get farm data from farm table
        raised = db.execute("SELECT SUM(raised) AS raised FROM farm WHERE user_id=?", user_id)

        needed = db.execute("SELECT SUM(needed) AS needed FROM farm WHERE user_id=?", user_id)

        farm = db.execute("SELECT * FROM farm WHERE user_id=? GROUP BY farm_name", user_id)

        # Get the total amount Invested in the farm by investors
        tot_inv = db.execute("SELECT SUM(amount) AS amount FROM transactions JOIN users ON users.id=transactions.user_id WHERE users.id=? AND transactions.deal=?", user_id, "Investment")

        # Query database for transactions table data
        trans = db.execute("SELECT * FROM transactions JOIN users ON users.id=transactions.user_id WHERE users.id=?", user_id)

        # Get the total amount for consultancy
        tot_amt = db.execute("SELECT SUM(amount) AS amount FROM transactions JOIN users ON users.id=transactions.user_id WHERE users.id=? AND transactions.deal=?", user_id, "Consultancy")

    # Check if user is an investor
    elif user_track == "Investor":

        # Get the total amount Invested in the farm by investors
        tot_inv = db.execute("SELECT SUM(amount) AS amount FROM transactions JOIN users ON users.id=transactions.user_id WHERE users.id=? AND transactions.deal=?", user_id, "Investment")

        # Get farm data from farm table
        farm = db.execute("SELECT * FROM farm JOIN transactions ON transactions.farm_name=farm.farm_name WHERE transactions.deal=?", "Investment")

        raised = ""
        needed = ""

        # Query database for transactions table data
        trans = db.execute("SELECT * FROM transactions JOIN users ON users.id=transactions.user_id WHERE users.id=?", user_id)

        # Get the total amount for consultancy
        tot_amt = db.execute("SELECT COUNT(amount) AS amount FROM transactions JOIN users ON users.id=transactions.user_id WHERE users.id=? AND transactions.deal=?", user_id, "Investment")

    # If user is a consultant
    else:

        # Get the total amount Invested in the farm by investors
        tot_inv = db.execute("SELECT COUNT(amount) AS amount FROM transactions JOIN users ON users.id=transactions.user_id WHERE users.id=? AND transactions.deal=?", user_id, "Consultancy")

        # Get farm data from farm table
        farm = db.execute("SELECT * FROM farm JOIN transactions ON transactions.farm_name=farm.farm_name WHERE transactions.deal=?", "Consultancy")

        raised = ""
        needed = ""

        # Query database for transactions table data
        trans = db.execute("SELECT * FROM transactions JOIN users ON users.id=transactions.user_id WHERE users.id=?", user_id)

        # Get the total amount for consultancy
        tot_amt = db.execute("SELECT SUM(amount) AS amount FROM transactions JOIN users ON users.id=transactions.user_id WHERE users.id=? AND transactions.deal=?", user_id, "Consultancy")

    # Render the dashboard html
    return render_template("dashboard.html", trans=trans, NGN=NGN, raised=raised, needed=needed, total=tot_amt, tot_inv=tot_inv, farm=farm)

# The support route
@app.route("/support", methods=["GET", "POST"])
@login_required
def support():
    """Show Support to User"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get submissions
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")

        # Validate submission
        if not email or email == "":
            return error("must provide an email")
        if not subject or subject == "":
            return error("must provide a subject")
        if not message or message == "":
            return error("must provide a message")

        # Send email
        msg = Message(subject, recipients=[email])
        msg.body = message
        mail.send(msg)

        return render_template("email.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Render the supprt html
        return render_template("support.html")


# The projects' farm route
@app.route("/farm/<farm_name>", methods=["GET"])
@login_required
def farm_update(farm_name):
    """Show farm details"""

    # Query database for particular farm table data
    farm = db.execute("SELECT * FROM farm WHERE farm_name=? GROUP BY farm_name ORDER BY date DESC", farm_name)

    # Query database for consultancy
    consul = db.execute("SELECT consultancy, transactions.date, username FROM transactions JOIN farm ON farm.farm_name=transactions.farm_name JOIN users ON users.id=transactions.user_id WHERE transactions.farm_name=?", farm_name)

    # Remember the update value from the farm table
    session["update"] = farm[0]["update"]

    # Query database for farm table data
    farms = db.execute("SELECT * FROM farm GROUP BY farm_name")

    # Render the farm html
    return render_template("farm.html", consul=consul, farm=farm, farms=farms, NGN=NGN, farm_name=farm_name, update=update)

# Upload route
@app.route("/uploads", methods=["GET", "POST"])
@login_required
def uploads():
    """Upload your farms' details"""
    # Remember user
    user_id = session["user_id"]

    # Remember user track
    user_track = session["track"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure user is a farmer
        if user_track == "Farmer":
            # Get the farm_name
            farm_name = request.form.get("farm_name")

            # Check if the post request has the images' part
            if 'image' not in request.files or 'cover_photo' not in request.files or 'pix_1' not in request.files or 'pix_2' not in request.files or 'pix_3' not in request.files or 'desc_img' not in request.files:
                # Flash a no image part message
                flash("No image part")

                # Redirect to the requested url
                return redirect(request.url)

            try:
                # Get farm image from the form
                image = request.files.get("image")

                # If the user does not select an image, the browser submits an empty file without a filename
                if image.filename == "":
                    flash("No image selected")

                    return redirect(request.url)

                # Get allowable extensions
                extensions = os.path.splitext(image.filename)[1].lower()

                # Check if images are with allowable extensions
                if extensions not in app.config["ALLOWED_EXTENSIONS"]:
                    return error("Unsupported extension type")

                # Ensure an image with the allowable extensions is selected
                if image and extensions in app.config["ALLOWED_EXTENSIONS"]:
                    # Get a secure filename for every selected image
                    filename = secure_filename(image.filename)

                    # Define file path for all images
                    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

                    # Save all images in the respective file paths
                    image.save(filepath)

            except RequestEntityTooLarge:
                return ("Image must not exceed 100kb in size", 413)

            try:
                # Get farm cover image from the form
                cover_photo = request.files.get("cover_photo")

                if cover_photo.filename == "":
                    flash("No cover photo selected")

                    return redirect(request.url)

                extensions_0 = os.path.splitext(cover_photo.filename)[1].lower()

                if extensions_0 not in app.config["ALLOWED_EXTENSIONS"]:
                    return error("Unsupported extension type")

                if cover_photo and extensions_0 in app.config["ALLOWED_EXTENSIONS"]:
                    filename_0 = secure_filename(cover_photo.filename)

                    filepath_0 = os.path.join(
                        app.config["UPLOAD_FOLDER"], filename_0)

                    cover_photo.save(filepath_0)

            except RequestEntityTooLarge:
                return ("Image must not exceed 100kb in size", 413)

            try:
                # Get farm pix_1 from the form
                pix_1 = request.files.get("pix_1")

                if pix_1.filename == "":
                    flash("No pix 1 selected")

                    return redirect(request.url)

                extensions_1 = os.path.splitext(pix_1.filename)[1].lower()

                if extensions_1 not in app.config["ALLOWED_EXTENSIONS"]:
                    return error("Unsupported extension type")

                if pix_1 and extensions_1 in app.config["ALLOWED_EXTENSIONS"]:

                    filename_1 = secure_filename(pix_1.filename)

                    filepath_1 = os.path.join(app.config["UPLOAD_FOLDER"], filename_1)

                    pix_1.save(filepath_1)

            except RequestEntityTooLarge:
                return ("Image must not exceed 100kb in size", 413)

            try:
                # Get farm pix_2 from the form
                pix_2 = request.files.get("pix_2")

                if pix_2.filename == "":
                    flash("No pix 2 selected")

                    return redirect(request.url)

                extensions_2 = os.path.splitext(pix_2.filename)[1].lower()

                if extensions_2 not in app.config["ALLOWED_EXTENSIONS"]:
                    return error("Unsupported extension type")

                if pix_2 and extensions_2 in app.config["ALLOWED_EXTENSIONS"]:

                    filename_2 = secure_filename(pix_2.filename)

                    filepath_2 = os.path.join(
                        app.config["UPLOAD_FOLDER"], filename_2)

                    pix_2.save(filepath_2)

            except RequestEntityTooLarge:
                return ("Image must not exceed 200kb in size", 413)

            try:
                # Get farm pix_3 from the form
                pix_3 = request.files.get("pix_3")

                if pix_3.filename == "":
                    flash("No pix 3 selected")

                    return redirect(request.url)

                extensions_3 = os.path.splitext(pix_3.filename)[1].lower()

                if extensions_3 not in app.config["ALLOWED_EXTENSIONS"]:
                    return error("Unsupported extension type")

                if pix_3 and extensions_3 in app.config["ALLOWED_EXTENSIONS"]:

                    filename_3 = secure_filename(pix_3.filename)

                    filepath_3 = os.path.join(
                        app.config["UPLOAD_FOLDER"], filename_3)

                    pix_3.save(filepath_3)

            except RequestEntityTooLarge:
                return ("Image must not exceed 200kb in size", 413)

            try:
                # Get farm description image from the form
                desc_img = request.files.get("desc_img")

                if desc_img.filename == "":
                    flash("No desc image selected")

                    return redirect(request.url)

                extensions_4 = os.path.splitext(desc_img.filename)[1].lower()

                if extensions_4 not in app.config["ALLOWED_EXTENSIONS"]:
                    return error("Unsupported extension type")

                if desc_img and extensions_4 in app.config["ALLOWED_EXTENSIONS"]:

                    filename_4 = secure_filename(desc_img.filename)

                    filepath_4 = os.path.join(
                        app.config["UPLOAD_FOLDER"], filename_4)

                    desc_img.save(filepath_4)

            except RequestEntityTooLarge:
                return ("Image must not exceed 200kb in size", 413)

            # Get farm description from the form
            description = request.form.get("description")

            # Get amount farmer needs to raise from the form
            needed = request.form.get("needed")

            # Get amount farmer has raised from the form
            raised = request.form.get("raised")

            # Get The full project description from the form
            proj_description = request.form.get("proj_description")

            # Get The project update from the form
            update = request.form.get("update")

            # Get the current date and time
            date = datetime.now()

            # Ensure farm name is filled
            if not farm_name:
                return error("Must provide farm name")

            # Ensure a brief description of the farm is keyed in
            if not description:
                return error("must give a brief farm description")

            # Ensure amount farmer needs is filled
            if not needed:
                return error("must provide amount needed by the farm")

            # Ensure amount farmer has raised is filled
            if not raised:
                return error("must provide amount the farmer raised")

            # Insert the form values to the farm table if the farm doesn't exist
            db.execute("INSERT INTO farm (user_id, farm_name, image, description, needed, raised, cover_photo, proj_description, pix_1, pix_2, pix_3, desc_img, date, update) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", user_id, farm_name, filename, description, needed, raised, filename_0, proj_description, filename_1, filename_2, filename_3, filename_4, date, update)

            # Save the farm_name in the session
            session["farm_name"] = farm_name

            # Redirect user to projects page
            return redirect("/projects")

        elif user_track == "Investor":

            # Redirect user to fund route
            return redirect("/fund")

        elif user_track == "Consultant":

            # Redirect user to consult route
            return redirect("/consult")

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        return render_template("uploads.html", user_track=user_track)


# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get username from the form
        username = request.form.get("username")

        # Get password from the form
        password = request.form.get("password")

        # Ensure username was submitted
        if not username:
            return error("must provide a username or email", 403)

        # Ensure password was submitted
        elif not password:
            return error("must provide password", 403)

        # Query database for username or password
        rows = db.execute("SELECT * FROM users WHERE username = ? OR email = ?", username, username)

        # Ensure username or email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return error("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Remember the track chosen by user
        session["track"] = rows[0]["track"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# Logout route
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# Contact route
@app.route("/contact")
@login_required
def contact():
    """Show farmfund's contacts"""

    # Render contact.html
    return render_template("contact.html")


# Register route
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get username
        username = request.form.get("username")

        # Get email
        email = request.form.get("email").lower()

        # Get password
        password = request.form.get("password")

        # Get confirmation
        confirmation = request.form.get("confirmation")

        # Get username
        track = request.form.get("track")

        # Ensure username was submitted
        if not username:
            return error("must provide username")

        # Ensure track was selected
        if not track:
            return error("must choose track")

        # Ensure username was submitted
        elif not email:
            return error("must provide email")

        # Ensure password was submitted
        elif not password:
            return error("must provide password")

        # Ensure password was confirmed
        elif not confirmation:
            return error("must confirm password")

        # Ensure passwords match
        elif password != confirmation:
            return error("password doesn't match")

        # The condition for every email
        regX = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"

        # Compile regex
        mail = re.compile(regX)

        # Search through the regex
        valid_mail = re.search(mail, email)

        # Validate
        if valid_mail:
            email = email
        else:
            return error("incorrect email syntax. See johndoe@gmail.com")

        # The condition for every password
        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,16}$"

        # Compile regex
        passwd = re.compile(reg)

        # Search through the regex
        soft = re.search(passwd, password)

        # Validate
        if soft:
            hash = generate_password_hash(password)

            # Insert the form values to the database if the username is not in use
            try:
                db.execute("INSERT INTO users (username, email, hash, track) VALUES(?, ?, ?, ?)", username, email, hash, track)
            except ValueError:
                return error("User already exists")

            # Redirect user to login page
            return redirect("/login")

        else:
            return error("password must contain atleast '1 upper case and 1 lower case letters, 1 number, 1 special symbol' & should be 6 to 16 characters long.")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


# Services route
@app.route("/services")
@login_required
def services():
    """Show farm services"""
    return render_template("services.html")


# Sell route
@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return error("TODO")


# Settings route
@app.route("/settings")
@login_required
def settings():
    """Show page settings"""
    # Remember user
    user_id = session["user_id"]

    # Query users table for username
    user = db.execute("SELECT username FROM users WHERE id=?", user_id)

    # Get the username from users database
    username = user[0]["username"]

    # Render settings.html
    return render_template("settings.html", username=username)


# User account route
@app.route("/useraccount")
@login_required
def useraccount():
    """Show user account details"""
    # Remember user
    user_id = session["user_id"]

    # Query users table for username
    user = db.execute("SELECT * FROM users WHERE id=?", user_id)

    # Get the username from users database
    username = user[0]["username"]

    # Get the user's track from users database
    track = user[0]["track"]

    # Get the user's email address from users database
    email = user[0]["email"]


    # Render settings.html
    return render_template("useraccount.html", username=username, track=track, email=email)

# Update user password route
@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    """Update user password"""
    # Remember user
    user_id = session["user_id"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Require the old password
        old_password = request.form.get("old_password")

        # Get the new password
        new_password = request.form.get("new_password")

        # Get password confirmation
        confirmation = request.form.get("confirmation")

        # Ensure old password was submitted
        if not old_password:
            return error("must provide password")

        # Ensure new password was submitted
        elif not new_password:
            return error("must enter a new password")

        # Ensure password was confirmed
        elif not confirmation:
            return error("must confirm password")

        # Ensure passwords match
        elif new_password != confirmation:
            return error("password doesn't match")

        # The condition for every password
        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,16}$"

        # Compile regex
        passwd = re.compile(reg)

        # Search through the regex
        soft = re.search(passwd, new_password)

        # Query the user's table for the username
        user = db.execute("SELECT username FROM users WHERE id=?", user_id)

        # Get user's name
        username = user[0]["username"]

        # Validate
        if soft:
            hash = generate_password_hash(new_password)

            # Insert the form values to the database if the username is not in use
            db.execute("UPDATE users SET username=?, hash=? WHERE id=?", username, hash, user_id)

            # Redirect user to login page
            return redirect("/login")

        else:
            return error("password must contain atleast '1 upper case and 1 lower case letters, 1 number, 1 special symbol' & should be 6 to 16 characters long.")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Render settings.html
        return render_template("updatepassword.html")


# Fund route
@app.route("/fund", methods=["GET", "POST"])
@login_required
def fund():
    """Fund farmer"""
    # Recall the user's id
    user_id = session["user_id"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get the amount you want to add
        cash = request.form.get("cash")

        # Ensure cash is not empty
        if cash == "":
            return error("must provide cash")

        # Ensure cash is a number
        if cash.isalpha() or not int(cash):
            return error("invalid parameter")

        # Ensure cash is a positive integer
        if int(cash) <= 0:
            return error("cash must be more than 0")

        # Get the name of the farm user wants to fund
        farm_name = request.form.get("farm_name")

        # Ensure farm name is not empty
        if farm_name == "":
            return error("must enter farm name")

        # Query farmer's raised amount from farm database
        farm = db.execute("SELECT * FROM farm WHERE farm_name=?", farm_name)

        user_cash = farm[0]['raised']

        current_cash = int(cash) + user_cash

        deal = "Investment"

        date = datetime.now()

        # Add the amount to the farmer's farm table
        db.execute("UPDATE farm SET raised=? WHERE farm_name=?", current_cash, farm_name)

        # Populate the transactions table with the current transaction
        db.execute("INSERT INTO transactions (user_id, farm_name, amount, deal, date) VALUES(?, ?, ?, ?, ?)", user_id, farm_name, int(cash), deal, date)

        flash("Farm successfully funded!")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Get farm name from the farm table
        farms = db.execute("SELECT farm_name FROM farm GROUP BY farm_name")

        # Render cash.html
        return render_template("cash.html", farms=farms)


# Consult route
@app.route("/consult", methods=["GET", "POST"])
@login_required
def consult():
    """Consultation for farmer"""
    # Recall the user's id
    user_id = session["user_id"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get the consultancy advice
        consult = request.form.get("consult")

        # Ensure consult is not empty
        if not consult or consult == "":
            return error("must provide consult")

        # Get the amount you want to add
        amount = request.form.get("amount")

        # Ensure amount is not empty
        if amount == "":
            return error("must provide amount")

        # Ensure amount is a number
        if amount.isalpha() or not int(amount):
            return error("invalid parameter")

        # Ensure amount is a positive integer
        if int(amount) <= 0:
            return error("amount must be more than 0")

        # Get the name of the farm user wants to fund
        farm_name = request.form.get("farm_name")

        # Ensure farm name is not empty
        if not farm_name or farm_name == "":
            return error("must enter farm name")

        # Query farmer's farm database
        farm = db.execute("SELECT * FROM farm WHERE farm_name=?", farm_name)

        farmer_cash = farm[0]['raised']

        current_cash = farmer_cash - int(amount)

        deal = "Consultancy"

        date = datetime.now()

        # Add the amount to the farmer's farm table
        db.execute("UPDATE farm SET raised=? WHERE farm_name=?", current_cash, farm_name)

        # Populate the transactions table with the current transaction
        db.execute("INSERT INTO transactions (user_id, farm_name, amount, deal, date, consultancy) VALUES(?, ?, ?, ?, ?, ?)", user_id, farm_name, int(amount), deal, date, consult)

        flash("Farm consultancy successfully offered!")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Get farm name from the farm table
        farms = db.execute("SELECT farm_name FROM farm GROUP BY farm_name")

        # Render consult.html
        return render_template("consult.html", farms=farms)