##### IMPORTS #####

from turtle import clear
from flask import Flask, request, render_template, redirect, url_for, session, flash, get_flashed_messages
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
import subprocess
from functools import wraps
import json
from numpy import var
import utils

##### GLOBAL VARIABLES #####

# initialising Flask object
app = Flask(__name__)
# intialising the LoginManager object
login_manager = LoginManager()
# ???
login_manager.init_app(app)
# ???
login_manager.login_view = ''
# setting secret key to use sessions
app.config['SECRET_KEY'] = "gradenewscope"
# student_dict maps a student_email to student_username, student_password and the
# wallet created for them
student_dict = {}
# teacher_dict maps a student_email to student_username, student_password and the
# wallet created for them
teacher_dict = {
    'teacher@gmail.com': {
        'uname': 'teacher',
        'pwd': 'teacherpwd',
        'wallet': 'teacher@gmail.com'
    }
}
# DEBUG should be true when app is in development server
DEBUG = True
# ???
ACCESS = {
    'student': 0,
    'teacher': 1
}
# location of local hyperledger fabric folder
FABRIC_DIR = "/Users/satyakinkohli/Desktop/Ashoka/Blockchain/blockchain-final-project/fabric/gradenewscope/javascript"
# location of local node executable
NODE_PATH = "/usr/local/bin/node"
# check if admin has been enrolled or not
adminEnrolled = False

##### FUNCTIONS #####

# homepage() - renders the homepage


@app.route("/")
def homepage():
    return render_template("homepage.html")


# login_register_post() - begins the process of sign in or sign up
@app.route('/', methods=['POST'])
def login_register_post():
    if request.form['welcomeuser'] == 'Sign In':
        if request.form['email'] in student_dict and student_dict[request.form['email']]['pwd'] == request.form['passwd']:
            session.pop('email', None)
            session['email'] = request.form['email']
            session.pop('uname', None)
            session['uname'] = request.form['uname']
            login_user(User(request.form['email']))
            return redirect(user_type(request.form['email']))
        elif request.form['email'] in teacher_dict and teacher_dict[request.form['email']]['pwd'] == request.form['passwd']:
            session.pop('email', None)
            session['email'] = request.form['email']
            session.pop('uname', None)
            session['uname'] = request.form['uname']
            login_user(User(request.form['email']))
            return redirect(user_type(request.form['email']))
        else:
            flash('Incorrect email/password')
            return redirect('/')
    elif request.form['welcomeuser'] == 'Sign Up':
        response = handle_setup(request.form)
        if response == "success":
            flash('Registration successful!', 'success')
            return redirect('/')
        else:
            flash('Registration failed! You are already registered', 'error')
            return redirect('/')
    else:
        print("Error! - 1")


# handle_setup() - registers the student in the gradenewscope portal, part I
def handle_setup(form_data):
    student_email = form_data['email']
    student_username = form_data['uname']
    student_pwd = form_data['passwd']

    # registerAdmin function runs registerAdmin.js and makes a physical wallet for the admin
    global adminEnrolled
    if not adminEnrolled:
        result = registerAdmin()
        if result is False:
            return "failure"
    adminEnrolled = True

    # if user already exists OR if no more wallets (max: 50) available, fail
    if (student_email in student_dict) or (len(student_dict) > 50):
        return "failure"
    # else assign the user a wallet
    else:
        # populate student_dict with data of the new student
        student_dict[student_email] = {
            "uname": student_username,
            "pwd": student_pwd,
            "wallet": student_email
        }
        # registerUser function runs registerUser.js and makes a physical wallet for the student
        if registerUser(student_dict[student_email]['wallet']) is not True:
            student_dict.pop(student_email)
            return "failure"
        # utils.write_file(db_path, json.dumps(student_dict))
        return "success"


# registerUser() - registers the student in the gradenewscope portal, part II
def registerUser(user):
    registerUserStatus = "None"

    try:
        registerUserStatus = subprocess.check_output(
            [NODE_PATH, FABRIC_DIR + "/registerUser.js", user], cwd=FABRIC_DIR).decode().split()
    except:
        pass

    if DEBUG:
        print(' '.join(registerUserStatus))

    if registerUserStatus != "None" and registerUserStatus[len(registerUserStatus) - 1] == "wallet":
        return True
    else:
        return False


# registerAdmin() - registers the admin in the gradenewscope portal
def registerAdmin():
    adminEnrollStatus = "None"

    try:
        adminEnrollStatus = subprocess.check_output(
            [NODE_PATH, FABRIC_DIR + "/enrollAdmin.js"], cwd=FABRIC_DIR).decode().split()
    except:
        pass

    if DEBUG:
        print(' '.join(adminEnrollStatus))

    if adminEnrollStatus != "None" and adminEnrollStatus[len(adminEnrollStatus) - 1] == "wallet":
        return True
    else:
        return False


# class User: assigns access level to each user
class User(UserMixin):
    def __init__(self, id, access=ACCESS['teacher']):
        self.id = id
        if id in student_dict:
            self.access = ACCESS['student']
        elif id in teacher_dict:
            self.access = ACCESS['teacher']
        else:
            # print("Error! - 2")
            pass


# user_type(): returns the url of the page to be redirected to, depending on whether
# the user is a student or a teacher
def user_type(email):
    if email in student_dict:
        return '/student_home'
    elif email in teacher_dict:
        return '/teacher_home'
    else:
        print("Error! - 3")


# load_user() - returns the User object given the user_id (the email in our case)
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


# requires_access_level() - makes a function to check if a particular user has access to
# visit that webpage
def requires_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = load_user(session['email'])
            if user.access != access_level:
                return render_template('response.html', response="Operation not authorized!")
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# student_home(): renders the student homepage
@app.route('/student_home', methods=['GET', 'POST'])
@login_required
@requires_access_level(ACCESS['student'])
def student_home():
    if request.method == 'POST':
        flash('' + session['uname'])
        if request.form['student_submit'] == 'Submit Answer':
            print("Submit Answer")
        elif request.form['student_submit'] == 'Query Assignment':
            print("Query Assignment")
        else:
            print("Query All Assignments")
        print(request.form['student_id'])
        return render_template('student_homepage.html')
    else:
        return render_template('student_homepage.html', username=session['uname'], email=session['email'])


# teacher_home(): renders the teacher homepage
@app.route('/teacher_home', methods=['GET', 'POST'])
@login_required
@requires_access_level(ACCESS['teacher'])
def teacher_home():
    if request.method == 'POST':
        flash('' + session['uname'])
        if request.form['teacher_submit'] == 'Submit Grade':
            print("Submit Grade")
        elif request.form['teacher_submit'] == 'Query Graded Assignment':
            print("Query Graded Assignment")
        else:
            print("Query All Graded Assignments")
        print(request.form['teacher_id'])
        return render_template('teacher_homepage.html')
    else:
        print(session['uname'])
        return render_template('teacher_homepage.html', username=session['uname'], email=session['email'])


if __name__ == "__main__":
    app.run(debug=True)
