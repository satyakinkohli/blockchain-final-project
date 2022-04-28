def query(input_string):
    new_input_string = input_string[0:-18]
    list_format = eval(new_input_string)
    return list_format[0]

#print(query('{"assignment_content":"content1","assignment_id":"1","final_score":"57"}. Query successful'))

def queryAll(input_string):
    new_input_string = input_string[0:-18]
    list_format = eval(new_input_string)
    return list_format

#print(queryAll('[{"assignment_content":"content1","assignment_id":"1","final_score":"57"}]. Query successful'))

def queryUngraded(input_string):
    new_input_string = input_string[0:-18]
    list_format = eval(new_input_string)
    return list_format

# print(queryUngraded('[{"assignment_content":"content1","assignment_id":"2","userID":"x509::/OU=client+OU=org1+OU=department1/CN=student1::/C=US/ST=California/L=San Francisco/O=org1.example.com/CN=ca.org1.example.com"}]. Query successful'))

print(queryAll("[]. Query successful"))
