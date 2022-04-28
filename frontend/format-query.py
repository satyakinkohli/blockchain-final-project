# import re

# def query(string):
#     string = string[:-18]
#     if string.find("true") != -1:
#         sindex = string.find("true")
#         lindex = sindex + 4
#         modString = string[:sindex] + "True" + string[lindex:]
#     else:
#         sindex = string.find("false")
#         lindex = sindex + 5
#         modString = string[:sindex] + "False" + string[lindex:]
#     dictFormat = eval(modString)
#     return dictFormat

# # print(query('{"assignment_content":"qwerty","assignment_id":"1","final_score":"30","high_deviation":true,"range_of_scores":80}. Query successful'))


# def queryAll(string):
#     string = string[:-18]
#     trueResults = [_.start() for _ in re.finditer("true", string)]
#     for index in trueResults:
#         string = string[:index] + "True" + string[index+4:]
#     falseResults = [_.start() for _ in re.finditer("false", string)]
#     for index in falseResults:
#         string = string[:index] + "False" + string[index+5:]
#     listFormat = eval(string)
#     return listFormat

# # print(queryAll('[{"assignment_content":"qwerty","assignment_id":"1","final_score":"50","high_deviation":true,"range_of_scores":80},{"assignment_content":"abcdef","assignment_id":"2","final_score":"94","high_deviation":false,"range_of_scores":-2}]. Query successful'))


def queryUngraded(input_string):
    new_input_string = input_string[:-18]
    list_format = eval(new_input_string)
    return list_format

res = queryUngraded('[{"assignment_content":"qwerty","assignment_id":"1","userID":"x509::/OU=client+OU=org1+OU=department1/CN=s1@student.com::/C=US/ST=California/L=SanFrancisco/O=org1.example.com/CN=ca.org1.example.com"},{"assignment_content":"abcdef","assignment_id":"2","userID":"x509::/OU=client+OU=org1+OU=department1/CN=s1@student.com::/C=US/ST=California/L=SanFrancisco/O=org1.example.com/CN=ca.org1.example.com"}]. Query successful')

def gettingActualUserID(dictData):
    for item in dictData:
        userID = item['userID']
        endOfEmail = userID.find('@student.com') + 12
        userID_secondHalf = userID[endOfEmail:]
        startOfEmail = len("x509::/OU=client+OU=org1+OU=department1/CN=")
        userID_firstHalf = userID[:startOfEmail]
        actualUserID = userID[startOfEmail:endOfEmail]
        item['userID'] = actualUserID
        print(item['userID'])

gettingActualUserID(res)
print(res)
