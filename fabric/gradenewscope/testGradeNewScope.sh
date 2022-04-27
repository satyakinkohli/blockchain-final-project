# teardown GradeNewScope
./teardownGradeNewScope.sh
# start GradeNewScope
./startGradeNewScope.sh

# changing directory to `javascript`
cd javascript

# registering users
node registerUser.js student1
node registerUser.js student2
node registerUser.js teacher1
node registerUser.js teacher2
node registerUser.js teacher3
node registerUser.js teacher4
node registerUser.js teacher5

# students submit assignments
node invoke.js submitAssignment student1 1 content1
node invoke.js submitAssignment student2 1 content2

# teachers submit grades
node invoke.js submitScore teacher1 "x509::/OU=client+OU=org1+OU=department1/CN=student1::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com" 1 78
node invoke.js submitScore teacher2 "x509::/OU=client+OU=org1+OU=department1/CN=student1::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com" 1 57
node invoke.js submitScore teacher3 "x509::/OU=client+OU=org1+OU=department1/CN=student1::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com" 1 89
node invoke.js submitScore teacher4 "x509::/OU=client+OU=org1+OU=department1/CN=student1::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com" 1 42
node invoke.js submitScore teacher5 "x509::/OU=client+OU=org1+OU=department1/CN=student1::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com" 1 35

node invoke.js submitScore teacher1 "x509::/OU=client+OU=org1+OU=department1/CN=student2::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com" 1 56
node invoke.js submitScore teacher2 "x509::/OU=client+OU=org1+OU=department1/CN=student2::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com" 1 34
node invoke.js submitScore teacher3 "x509::/OU=client+OU=org1+OU=department1/CN=student2::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com" 1 67
node invoke.js submitScore teacher4 "x509::/OU=client+OU=org1+OU=department1/CN=student2::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com" 1 23
node invoke.js submitScore teacher5 "x509::/OU=client+OU=org1+OU=department1/CN=student2::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com" 1 95

# student queries a specific assignment they have submitted earlier
node query.js queryAssignment student1 1
node query.js queryAssignment student2 1

# student submits another assignment
node invoke.js submitAssignment student1 2 content1

# teachers again submit grades
node invoke.js submitScore teacher1 "x509::/OU=client+OU=org1+OU=department1/CN=student1::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com" 3 87
node invoke.js submitScore teacher2 "x509::/OU=client+OU=org1+OU=department1/CN=student1::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com" 3 75
node invoke.js submitScore teacher3 "x509::/OU=client+OU=org1+OU=department1/CN=student1::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com" 3 98
node invoke.js submitScore teacher4 "x509::/OU=client+OU=org1+OU=department1/CN=student1::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com" 3 24
node invoke.js submitScore teacher5 "x509::/OU=client+OU=org1+OU=department1/CN=student1::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com" 3 53

# student queries all assignments they have submitted in the past
node query.js queryAllAssignments student1

# teacher queries all assignments which they have not graded as of now
node query.js teacherQueryUngraded teacher1