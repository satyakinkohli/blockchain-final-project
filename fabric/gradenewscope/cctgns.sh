# teardown GradeNewScope
./teardownGradeNewScope.sh
# start GradeNewScope
./startGradeNewScope.sh

# changing directory to `javascript`
cd javascript

# enroll the admin
node enrollAdmin.js

# registering users
node registerUser.js student1
node registerUser.js teacher1
node registerUser.js teacher2
node registerUser.js teacher3
node registerUser.js teacher4
node registerUser.js teacher5

# student1 submits assignment1
node invoke.js submitAssignment student1 1 content1

# student1 submits assignment1 again
node invoke.js submitAssignment student1 1 content1

# student1 queries assignment1
node query.js queryAssignment student1 1

# student1 queries all assignments
node query.js queryAllAssignments student1

# teache5 queries all assignments which they have not graded as of now
node query.js teacherQueryUngraded teacher5

# teachers submit grades
node invoke.js submitScore teacher1 "x509::/OU=client+OU=org1+OU=department1/CN=student1::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com" 1 78
node invoke.js submitScore teacher2 "x509::/OU=client+OU=org1+OU=department1/CN=student1::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com" 1 57
node invoke.js submitScore teacher3 "x509::/OU=client+OU=org1+OU=department1/CN=student1::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com" 1 89
node invoke.js submitScore teacher4 "x509::/OU=client+OU=org1+OU=department1/CN=student1::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com" 1 42
node invoke.js submitScore teacher5 "x509::/OU=client+OU=org1+OU=department1/CN=student1::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com" 1 35

# teacher5 submits a grade again
node invoke.js submitScore teacher5 "x509::/OU=client+OU=org1+OU=department1/CN=student1::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com" 1 35

# student queries assignment1
node query.js queryAssignment student1 1

# student queries all assignments they have submitted in the past
node query.js queryAllAssignments student1

# teacher5 queries all assignments which they have not graded as of now
node query.js teacherQueryUngraded teacher5