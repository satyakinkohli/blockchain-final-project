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
teacher_dict = {}
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
            print("here")
            login_user(User(request.form['email']))
            print("here too")
            return redirect(user_type(request.form['email']))
        else:
            flash('Incorrect email/password')
            return redirect('/')
    elif request.form['welcomeuser'] == 'Sign Up':
        response = handle_setup(request.form)
        if response == "success":
            session.pop('email', None)
            session['email'] = request.form['email']
            session.pop('uname', None)
            session['uname'] = request.form['uname']
            login_user(User(request.form['email']))
            return redirect(user_type(request.form['email']))
        else:
            flash('Registration failed! You are already registered', 'error')
            return redirect('/')
    else:
        pass


# handle_setup() - registers the student in the gradenewscope portal, part I
def handle_setup(form_data):
    email = form_data['email']
    username = form_data['uname']
    password = form_data['passwd']

    # fabric_registerAdmin function runs registerAdmin.js and makes a physical wallet for the admin
    global adminEnrolled
    if not adminEnrolled:
        result = fabric_registerAdmin()
        if result is False:
            return "failure"
    adminEnrolled = True

    # if student already exists OR if there are more than 50 students, fail
    if (email in student_dict) or (len(student_dict) > 50):
        return "failure"
    # if teacher already exists OR if there are more than 5 teachers, fail
    elif (email in teacher_dict) or (len(teacher_dict) > 5):
        return "failure"
    # else assign the user a wallet
    else:
        if email[-11:-4] == "student":
            # populate student_dict with data of the new student
            student_dict[email] = {
                "uname": username,
                "pwd": password,
                "wallet": email
            }
            # fabric_registerUser function runs registerUser.js and makes a physical wallet for the student
            if fabric_registerUser(student_dict[email]['wallet']) is not True:
                student_dict.pop(email)
                return "failure"
            # utils.write_file(db_path, json.dumps(student_dict))
            return "success"
        elif email[-11:-4] == "teacher":
            # populate teacher_dict with data of the new student
            teacher_dict[email] = {
                "uname": username,
                "pwd": password,
                "wallet": email
            }
            # fabric_registerUser function runs registerUser.js and makes a physical wallet for the student
            if fabric_registerUser(teacher_dict[email]['wallet']) is not True:
                teacher_dict.pop(email)
                return "failure"
            # utils.write_file(db_path, json.dumps(teacher_dict))
            return "success"
        else:
            return "failure"


# fabric_registerUser() - registers the student in the gradenewscope portal, part II
def fabric_registerUser(user):
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


# fabric_registerAdmin() - registers the admin in the gradenewscope portal
def fabric_registerAdmin():
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
            pass


# user_type(): returns the url of the page to be redirected to, depending on whether
# the user is a student or a teacher
def user_type(email):
    if email in student_dict:
        return '/student_home'
    elif email in teacher_dict:
        print("here again")
        return '/teacher_home'
    else:
        pass


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
        var = {}
        var.clear()
        var = {'email': request.form['student_id'],
               'username': student_dict[request.form['student_id']]['uname']}
        if request.form['student_submit'] == 'Submit Assignment':
            assignment_id = request.form['assignment_id']
            assignment_content = request.form['assignment_content']
            submitAssignmentResult = fabric_submitAssignment(
                var['email'], assignment_id, assignment_content)
            if submitAssignmentResult is True:
                var['submit_assignment_status'] = "You have submitted your assignment successfully!"
            else:
                var['submit_assignment_status'] = "Failed to submit the assignment. You might be attempting to re-submit the assignment."
        elif request.form['student_submit'] == 'Query Assignment':
            assignment_id = request.form['assignment_id']
            queryAssignmentResult, queryAssignmentOutput = fabric_queryAssignment(
                var['email'], assignment_id)
            if queryAssignmentResult is True:
                var['queryAssignmentOutput'] = queryAssignmentOutput
            else:
                var['queryAssignmentOutput'] = "Your assignment has not been evaluated yet, maybe wait a bit more?"
        else:
            queryAllAssignmentsResult, queryAllAssignmentsOutput = fabric_queryAllAssignments(
                var['email'])
            if queryAllAssignmentsResult is True:
                if queryAllAssignmentsOutput == []:
                    var['queryAllAssignmentsOutput'] = "No assignment has been evaluated until now"
                else:
                    var['queryAllAssignmentsOutput'] = queryAllAssignmentsOutput
            else:
                var['queryAllAssignmentsOutput'] = "QueryAllAssignments Unsucessful."
        return render_template('student_homepage.html', **var)
    else:
        return render_template('student_homepage.html', username=session['uname'], email=session['email'])


# teacher_home(): renders the teacher homepage
@app.route('/teacher_home', methods=['GET', 'POST'])
@login_required
@requires_access_level(ACCESS['teacher'])
def teacher_home():
    if request.method == 'POST':
        rav = {}
        rav.clear()
        rav = {'email': request.form['teacher_id'],
               'username': teacher_dict[request.form['teacher_id']]['uname']}

        if request.form['teacher_submit'] == 'Submit Grade':
            assignment_id = request.form['assignment_id']
            student_id = request.form['student_id']
            teacher_grade = request.form['teacher_grade']
            submitScoreResult = fabric_submitGrade(
                rav['email'], student_id, assignment_id, teacher_grade)
            if submitScoreResult is True:
                rav['submit_grade_status'] = "You have submitted your assignment grade successfully!"
            else:
                rav['submit_grade_status'] = "Failed to submit the assignment grade. You might be attempting to evaluate the assignment again"

        queryUngradedAssignmentResult, queryUngradedAssignmentOutput = fabric_queryUngradedAssignment(
            rav['email'])
        if queryUngradedAssignmentResult is True:
            if queryUngradedAssignmentOutput == []:
                rav['queryUngradedAssignmentOutput'] = "There is no assignment for you to grade right now."
            else:
                rav['queryUngradedAssignmentOutput'] = queryUngradedAssignmentOutput

        return render_template('teacher_homepage.html', **rav)
    else:
        ravtemp = {}
        ravtemp.clear()
        ravtemp = {'email': session['email'],
                   'username': teacher_dict[session['email']]['uname']}
        queryUngradedAssignmentResult, queryUngradedAssignmentOutput = fabric_queryUngradedAssignment(
            ravtemp['email'])
        if queryUngradedAssignmentResult is True:
            if queryUngradedAssignmentOutput == []:
                ravtemp['queryUngradedAssignmentOutput'] = "There is no assignment for you to grade right now."
            else:
                ravtemp['queryUngsradedAssignmentOutput'] = queryUngradedAssignmentOutput
        else:
            ravtemp['queryUngradedAssignmentOutput'] = "Query Unsuccessful"
        return render_template('teacher_homepage.html', **ravtemp)


# student submits their assignment
def fabric_submitAssignment(email, assignment_id, assignment_content):
    submitAssignmentStatus = "None"

    try:
        submitAssignmentStatus = subprocess.check_output(
            [NODE_PATH, FABRIC_DIR + "/invoke.js", "submitAssignment", email, assignment_id, assignment_content], cwd=FABRIC_DIR).decode().split()
    except:
        pass

    if DEBUG:
        print(' '.join(submitAssignmentStatus))

    if submitAssignmentStatus == "None":
        return False
    elif submitAssignmentStatus[len(submitAssignmentStatus) - 1] != "submitted":
        return False
    else:
        return True


# student queries their assignment
def fabric_queryAssignment(email, assignment_id):
    queryAssignmentOutput = "None"

    try:
        queryAssignmentOutput = subprocess.check_output(
            [NODE_PATH, FABRIC_DIR + "/query.js", "queryAssignment", email, assignment_id], cwd=FABRIC_DIR).decode()
    except:
        pass

    if DEBUG:
        print(queryAssignmentOutput)

    if queryAssignmentOutput[-10:] != "successful":
        return False, ""
    else:
        return True, format_queryAssignment(queryAssignmentOutput)


# formats the output of the student queryAssignment
def format_queryAssignment(string):
    newString = string[0:-18]
    list_format = eval(newString)
    return list_format[0]


# student queries all their assignments
def fabric_queryAllAssignments(email):
    queryAllAssignmentsOutput = "None"

    try:
        queryAllAssignmentsOutput = subprocess.check_output(
            [NODE_PATH, FABRIC_DIR + "/query.js", "queryAllAssignments", email], cwd=FABRIC_DIR).decode()
    except:
        pass

    if DEBUG:
        print(queryAllAssignmentsOutput)

    if queryAllAssignmentsOutput == "None":
        return False, ""
    else:
        return True, format_queryAllAssignments(str(queryAllAssignmentsOutput))


# formats the output of the student queryAllAssignments
def format_queryAllAssignments(string):
    newString = string[0: -19]
    list_format = eval(newString)
    return list_format


# teacher submits an assignment grade
def fabric_submitGrade(email, student_id, assignment_id, score):
    submitGradeStatus = "None"

    try:
        submitGradeStatus = subprocess.check_output(
            [NODE_PATH, FABRIC_DIR + "/invoke.js", "submitScore", email, student_id, assignment_id, score], cwd=FABRIC_DIR).decode().split()
    except:
        pass

    if DEBUG:
        print(' '.join(submitGradeStatus))

    if submitGradeStatus == "None":
        return False
    elif submitGradeStatus[len(submitGradeStatus) - 1] != "submitted":
        return False
    else:
        return True


# teacher queries all their ungraded assignment grades
def fabric_queryUngradedAssignment(email):
    queryUngradedAssignmentOutput = "None"

    try:
        queryUngradedAssignmentOutput = subprocess.check_output(
            [NODE_PATH, FABRIC_DIR + "/query.js", "teacherQueryUngraded", email], cwd=FABRIC_DIR).decode()
    except:
        pass

    if DEBUG:
        print(' '.join(queryUngradedAssignmentOutput))

    if queryUngradedAssignmentOutput == "None":
        return False, ""
    elif (str(queryUngradedAssignmentOutput[-11:])).strip() == "successful":
        return True, format_queryUngradedAssignment(str(queryUngradedAssignmentOutput))
    else:
        return False, ""


# formats the output of the teacher queryUngradedAssignment
def format_queryUngradedAssignment(string):
    newString = string[0:-19]
    list_format = eval(newString)
    return list_format


# logout
@app.route('/logout')
@login_required
def logout():
    session.pop('email', None)
    session.pop('uname', None)
    logout_user()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
