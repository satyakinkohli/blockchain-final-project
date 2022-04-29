# blockchain-final-project

##### CS2361 Final Project: GradeNewScope

[Demo Video Recording](https://drive.google.com/file/d/1mLlvx75kZkOGq7sA_zat9AMJ5J1O1kJ5/view?usp=sharing)


## 1. Introduction ##
Grades play a huge role in defining students’ future. As a result, it is essential that grading is done fairly and consistently. Under the existing arrangements of grading, generally, one evaluator has complete control over the grade any student receives – this opens the possibility of bias. The evaluator can incorrectly grade a student in two ways, either by giving them a lower grade than they deserve or by giving them a higher grade than they deserve. Both these circumstances are unfair to either the student or to the rest of the student body in their own sense. However, even if multiple teachers grade a student’s paper and store the respective grades in a server, there is scope for rigging due to the centralized nature of such a system. Anything can be changed in the system as per the servers wish. In order to solve these problems, we propose our application GradeNewScope which is hosted on a blockchain network through the use of hyperledger fabric. 

The application allows students to upload their assignments/answer scripts which are then evaluated by all the professors independently and a final score is assigned to the student based on all these scores. Moreover, the application identifies if there is high deviation within the marks received by a student on a particular assignment. If there is indeed high deviation, it suggests that the scores are inconsistent.

The blockchain peer to peer network guarantees accountability, transparency and security. In case of high deviation in marks, teachers can be questioned and held accountable if there was any bias or carelessness. There is provision for an immutable ledger such that record of grades will always be available for public access and cannot be edited once included into a valid block. This ensures transparency. Students also have a sense of security because they know that there is no authority that can alter their records once their final score for a particular assignment has been calculated and pushed into the network.


## 2. Project Goals ##
Following from the introduction offered above, the project goals are as follows:
to ensure that students get assigned fair grades which justify their performance on the assignment/exams and reflect a broad consensus among the instructors regarding their grades.
to ensure professors are held accountable and face appropriate consequences for not marking in an objective manner as per the grading scheme


## 3. The Client-side working ##
To provide the functionalities promised in the above section, our application will need to have a certain structure with different components performing different jobs. Flow of the application - 

The first part is register/login. The user will be prompted for email id, username and password. They will have the option to either sign up or sign in. If one has already registered with these details, they can sign in otherwise sign up. For teachers, the email id must end in ‘@teacher.com’. Likewise, the email id for students must end in ‘@student.com’. Accordingly, the user is taken to the student or teacher portal. There will be exactly 5 teachers needed to be registered on the portal and there can be as many students as desired.

On the student portal, the student will have an option to upload their submission of an assignment. The student’s unique student_id, as well as the assignment’s unique assignment_id will be combined to form a combination_id which will uniquely identify a given student’s submission of a given assignment. Besides submitting an assignment, a student can query his previously submitted assignments to check the marks one has received. There is an option to query a particular assignment by giving the assignment id or query all the assignments. An assignment will only return as part of a query operation if it has already been evaluated by all 5 teachers. When all teachers have graded the submission of a student, the final score is calculated as the median of all the scores and the range of scores is calculated as the difference between the maximum and minimum scores. If this range is high (>10), the student’s particular assignment is identified as having high deviation.

On the teacher portal, the teacher will see a table where each row represents an assignment that he or she is yet to grade. That table will include the student id, assignment id and assignment content for the teacher to refer. Besides, there will be a functionality to submit the scores for a particular assignment of a particular student. The teacher will be prompted for assignment id, student id and marks. After a teacher has graded a particular assignment, he will no longer see this assignment in the table containing the list of ungraded assignments.


## 4. Application Rulebook ##
We make use of the following global variable in our chaincode:

Assign_combinations: A list containing the combination_id of all the assignments that have been submitted.

The asset is a key:value pair which is defined as follows:

| Key  | Value |
| ------------- | ------------- |
| (combination_id)  | Attempted_assignment = {assignment_id, assignment_content, num_evaluated, scores, range_of_scores, high_deviation, final_score, userID}  |

What each of these mean - 
- combination_id : It is the unique identifier of a student’s attempted assignment and it is obtained via the concatenation of assignment_id and userID of the student
- assignment_content : This is a string representing the student’s submission in textual format . Eg. “A: The reason for this is… , B: The most important factor is … , C: Turing’s contribution to … “
- num_evaluated: This is an integer variable which keeps count of the number of teachers who have evaluated and graded this assignment
- scores: This is a dictionary which maps the <teacher_id> with the score they gave to the student. Essentially, scores = {<teacher_id>: score}.
- range_of_scores: This is an integer which stores the difference between the maximum and minimum score that the student has received on that assignment.
- high_deviation: This is a boolean variable which is set to 1 if the range_of_scores > 10 and 0 otherwise
- final_score: This is an integer value which stores the final score the student receives. 
userID : This is an integer storing the userID of the student


## 5. Stack Used ##
The frontend was made using HTML and CSS, while the backend was managed using Flask, which is a Python web framework. We have taken inspiration from this [last year project](https://github.com/agrawalnandini/hyperfunds.git).


## 6. Chaincode Functions ##
_submitAssignment()_:
This function is called by a student. The arguments passed are ctx, assignment_id and assignment_content. The userID is derived from ctx.. 
- This function creates an attempted_assignment object corresponding to the given combination of assignment_id and userID and stores it onto the ledger state. 
- The assignment_content field of the attempted_assignment object is updated as per the given input to the function. The userID field is also updated. 
- The rest of the fields of the attempted_assignment object are defined as 0, empty or null and will only be updated when other functions are invoked
- A check is implemented to ensure that the combination_key is unique -> A student should not be allowed to submit the same assignment twice.

_queryAssignment()_:
This function is called by a student. The arguments passed are ctx, assignment_id and the tempuserID is derived from ctx.
- The function returns the attempted_assignment object associated with the combination_id (derived from assignment_id and tempuserId)
- Some of the fields are deleted which need not be shown to the student - scores dictionary, num_evaluated and userID)
- A check is implemented to ensure that the combination_id is valid.
- A check is also implemented to ensure that all the teachers have graded the assignment when the student tries to query it. If they haven’t, the students will not be able to query it.

_queryAllAssignments()_:
This function is called by a student. The only argument passed is ctx. tempuserID is derived from ctx.
- The function returns an array containing all the attempted_assignment objects associated with the derived tempuserID (studentID) given they have been evaluated by 5 teachers.
- Some of the fields are deleted from each object which need not be shown to the student - scores dictionary, num_evaluated and userID)

_teacherQueryUngraded()_:
This function is called by a teacher. The only argument passed is ctx. The teacher_id is derived.
- This function returns an array containing all the attempted_assignment where the scores dictionary does not contain the teacher id. These are the assignments which are yet to be graded by the teacher who is logged in.
- The fields of the attempted_assignment which are retained are userID, assignment_id and assignment_content.

_submitScore()_:
This function is called by a teacher. The arguments passed are ctx, student_id, assignment_id and marks. The teacher_id is derived from ctx.
- This function firstly updates the scores dictionary of the attempted_assignment object corresponding to the combination_id (derived by student_id and assignment_id). The teacher id is the key and the marks argument is the value.
- There is a check to ensure that the combination_id is valid.
- There is another check to ensure that this teacher hasn’t already graded this assignment
- The num_evaluated field of the attempted_assignment object is incremented by 1
- If num_evaluated equals the total number of teachers, it implies that all teachers have graded that assignment for the given student
- This is when the final score and the range of scores is calculated. 
- If the range of scores > 10, the high_deviation variable is set to true otherwise false.


## 7. Other Important Javascript Files ##

_enrollAdmin.js_: This file enrolls an admin to GradeNewScope. An admin is essential for the functioning of our application.

_registerUser.js_: This file registers a user to GradeNewScope A new wallet is subsequently created for the registrant. We have 2 types of users- teachers and students each having their respective portal for interacting with our application. This file is invoked with the email id submitted by the registrant.

_query.js_: This file is used to invoke 3 functions in the chaincode - queryAssignment(), queryAllAssignments() and teacherQueryUngraded() with the appropriate arguments. 

_invoke.js_: This file is used to invoke 2 functions in the chaincode - submitAssignment() and  submitScore() with the appropriate arguments. 


