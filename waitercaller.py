import datetime
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect	#Redirects the user to the URL specified
from flask import url_for	#Builts a URL from a function name
from flask.ext.login import LoginManager	#Flask-Extension-Class-LoginManager
from flask.ext.login import login_required	#Flask-Extension-login_required_decorator
from flask.ext.login import login_user		#Flask-Extension-login_user
from flask.ext.login import logout_user		#Flask-Extension-logout_user
from flask.ext.login import current_user	#Flask-Extension-current_user

from bitlyhelper import BitlyHelper	#Import the BitlyHelper class to shorten the URLs
import config
from mockdbhelper import MockDBHelper as DBHelper	#Import Mock-Database
from passwordhelper import PasswordHelper	#Import PasswordHelper-Class
from forms import LoginForm
from forms import RegistrationForm	#Import the forms we need
from forms import CreateTableForm
from user import User	#User-class for the login-function

DB = DBHelper()		#DB is a global instance to our Database MockDBHelper-Class (or real DBHelper)

PH = PasswordHelper()	#PH is a global instance to use the PasswordHelper class

BH = BitlyHelper()	#BH is a global instance to use the BitlyHelper class

app = Flask(__name__)
app.secret_key = 'GRyX5UPtDh6GojpVw+ixPql+W90o26AsvZNLRdVaSA48ly4snL'	#Secret key for the session cookies


login_manager = LoginManager(app)	#Create an instance of the LoginManager-Class with a reference to our application.
					#We will use this class to manage logins for our application.

@app.route("/")
def home():
    loginform = LoginForm()
    registrationform = RegistrationForm()	#Instance of our RegistrationForm class which we'll render to the template
    return render_template("home.html", loginform=loginform, registrationform=registrationform)
#Render to our Bootstrap template by default


@app.route("/login", methods=["POST"])
def login():
    form = LoginForm(request.form)	#Get access to all forms with request.form

    if form.validate():

        stored_user = DB.get_user(form.loginemail.data)

        if stored_user and PH.validate_password(form.loginpassword.data, stored_user['salt'], stored_user['hashed']):
												#To validate the password

            user = User(form.loginemail.data)
            login_user(user, remember=True)
            return redirect(url_for('account'))

        form.loginemail.errors.append("Email or password invalid")	#Add error message if EmailField vail validation.

    return render_template("home.html", loginform=form, registrationform=RegistrationForm())



@login_manager.user_loader	#Indicates, that Flask-Login handels users which already have a cooky
def load_user(user_id):	#The user_id from the cooky is passed to the load_user function
    user_password = DB.get_user(user_id)	#user_password variable stores the password from the Mock-Database
    if user_password:		#Checks if the user is in our database
        return User(user_id)	#Recreate the User object


@app.route("/logout")
def logout():				#Route and function for the logout
    logout_user()
    return redirect(url_for("home"))


@app.route("/register", methods=["POST"])
def register():
    loginform = LoginForm()
    form = RegistrationForm(request.form) #Instance of our form class. Request.form represent all input fields
    
    if form.validate(): #From the object form we call the validation check for the input fields. True if all pass
        if DB.get_user(form.email.data):	#Takes the input email and checks wether this email already is in our DB.
            form.email.errors.append("Email address already registered") #Adds an error message to the form object and
									 #there to the email part of the object.
            return render_template('home.html', loginform=loginform, registrationform=form)
									 #Render the content of the form object to the
									 #template with the error message email.
        salt = PH.get_salt()
        hashed = PH.get_hash(form.password2.data + salt)
        DB.add_user(form.email.data, salt, hashed)
        return render_template("home.html", loginform=loginform, registrationform=form,
            onloadmessage="Registration successful. Please log in.") #Render form object content to the home.html
								     #template and trigger the JavaScript popup.

    return render_template("home.html", loginform=loginform, registrationform=form)
					#If the validation check fail the function render
					#back to the home.html page



@app.route("/account")
@login_required			#The function will only than return to the user if the user is logged in
def account():
    createtableform = CreateTableForm()
    tables = DB.get_tables(current_user.get_id())
    return render_template("account.html", createtableform=createtableform, tables=tables)
			#Gets the tables from the database and passes the data with the form through to the template.


@app.route("/account/createtable", methods=["POST"])	#Subroute of the account page
@login_required
def account_createtable():	#This route function belongs to the account
    form = CreateTableForm(request.form)	#request.form to get access to all form-fields

    if form.validate():

        tableid = DB.add_table(form.tablenumber.data, current_user.get_id()) #Flask Login function to get
									     #the id of the current user
        new_url = BH.shorten_url(config.base_url + "newrequest/" + tableid) #Creates the table URL shortend by bitly.
        DB.update_table(tableid, new_url)
        return redirect(url_for('account'))

    return render_template("account.html", createtableform=form, tables=DB.get_tables(current_user.get_id()))



@app.route("/account/deletetable")
@login_required
def account_deletetable():
    tableid = request.args.get("tableid")	#Accepts the table ID that needs to be deleted and then ask the
    DB.delete_table(tableid)			#database(dbhelper) to delete it.
    return redirect(url_for('account'))





@app.route("/dashboard")
@login_required
def dashboard():
    now = datetime.datetime.now()
    requests = DB.get_requests(current_user.get_id())	#Get all requests from the logged in user.
    for req in requests:
        deltaseconds = (now - req['time']).seconds
        req['wait_minutes'] = "{}.{}".format((deltaseconds/60), str(deltaseconds % 60).zfill(2)) #The deltatime is added to
												 #the requests variable.
    return render_template("dashboard.html", requests=requests)



@app.route("/dashboard/resolve")
@login_required
def dashboard_resolve():
    request_id = request.args.get("request_id")
    DB.delete_request(request_id)	#Call the the delete_request methode with the correct request_id, which we have
    return redirect(url_for('dashboard'))	#from the hidden field in our template.




@app.route("/newrequest/<tid>")	#tid is the tableid
def new_request(tid):
    DB.add_request(tid, datetime.datetime.now())	#Create a new request in our database which contains the 
							#table id and current time.
    return "Your request has been logged and a waiter will be with you shortly"







if __name__ == '__main__':
    app.run(port=5000, debug=True)


