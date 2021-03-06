/*
 * SPDX-License-Identifier: Apache-2.0
 */

'use strict';

const {Contract} = require('fabric-contract-api');
const ClientIdentity = require('fabric-shim').ClientIdentity;

// Total teachers registered on the portal
let total_teachers = 5;

// list of combination ids that have already been submitted
let assign_combinations = [];

// list of users
let users = [];

let teacher1_email;
let teacher2_email;
let teacher3_email;
let teacher4_email;
let teacher5_email;

class GradeNewScope extends Contract {

    async initLedger(ctx, teacher1, teacher2, teacher3, teacher4, teacher5) {
        console.info('============= START : Initialize Ledger ===========');

        teacher1_email = teacher1;
        teacher2_email = teacher2;
        teacher3_email = teacher3;
        teacher4_email = teacher4;
        teacher5_email = teacher5;

        console.log(`Teacher 1 email : ${teacher1_email}`);
		console.log(`Teacher 2 email : ${teacher2_email}`);
        console.log(`Teacher 3 email : ${teacher3_email}`);
        console.log(`Teacher 4 email : ${teacher4_email}`);
        console.log(`Teacher 5 email : ${teacher5_email}`);

        const startKey = '0';
        const endKey = '99999';

        const iterator = await ctx.stub.getStateByRange(startKey, endKey);

        while (true) {
            const res = await iterator.next();

            if (res.value && res.value.value.toString()) {
                // console.log(res.value.value.toString('utf8'));
                let assignment_attempted;
                try {
                    assignment_attempted = JSON.parse(res.value.value.toString('utf8'));

                    // update users array 
                    if (assignment_attempted.assignment_content === "$HELLO$") {
                        users.push(assignment_attempted.userID);
                    }

                } catch (err) {
                    console.log(err);
                    assignment_attempted = res.value.value.toString('utf8');
                }
            }

            if (res.done) {
                await iterator.close();
                console.log(`users: ${users}`);
                console.log(`numUsers: ${users.length}`);
                //console.log(`lastListingID: ${listingID}`);
                break;
            }
        }
        console.info('============= END : Initialize Ledger ===========');
    }

    async submitAssignment(ctx, assignment_id, assignment_content) {
        console.info('============= START : submitAssignment ===========');

        let cid = new ClientIdentity(ctx.stub);
        let userID = cid.getID();

        console.log(`assignment_id : ${assignment_id}`);
	    console.log(`assignment_content : ${assignment_content}`);
        console.log(`userID  : ${userID}`);
        
        let combination_id;
        combination_id = (assignment_id.toString()).concat("-", userID.toString());

        if (assign_combinations.includes(combination_id)) {
            console.log("You have already submitted this assignment")
            throw new Error(`Combination_id : ${combination_id} already submitted`)
        }

        const scores = {}; // Dictionary to hold scores given by each teacher
        const final_score = null; // Final score of student
	    const range_of_scores = 0; // Integer holding value of Max - Min 
        const num_evaluated = 0; // Counter tracking how many teachers have evaluated this assignment for this student, run some code when counter reaches max_teachers
        const high_deviation = null;
        
        const attempted_assignment = {
            assignment_id,
            assignment_content,
            num_evaluated,
            scores,
            range_of_scores,
            high_deviation,
            final_score,
            userID
        };

        // // if new user, add user to users array
        // if (!(users.includes(userID))) {
        //     console.log(`New user! Added to users array.`);
        //     users.push(userID);
        // }

        assign_combinations.push(combination_id);
        
        await ctx.stub.putState(combination_id.toString(), Buffer.from(JSON.stringify(attempted_assignment)));
        console.info('============= END : submitAssignment ===========');
    }

    // If students call this function, they can see only their own assignment
    // If teachers call this function, they pass student email as argument and can see any student's assignment
    // To check if teacher has called -> userID.includes(teacher1_email) | userID.includes(teacher2_email) ....

    async queryAssignment(ctx, assignment_id) {
        console.info('============= START : queryAssignment ===========');
        let cid = new ClientIdentity(ctx.stub);
        let tempUserID = cid.getID();

        console.log(`assignment_id: ${assignment_id}`);
        console.log(`userID  : ${tempUserID}`);

        let combination_id;
        combination_id = (assignment_id.toString()).concat("-", tempUserID.toString());

        const attempted_assignmentAsBytes = await ctx.stub.getState(combination_id); // get the assignment from chaincode state
        if (!(attempted_assignmentAsBytes) || attempted_assignmentAsBytes.length === 0) {
            throw new Error(`${attempted_assignment} does not exist`);
        }
        
        let attempted_assignment;
        attempted_assignment = JSON.parse(attempted_assignmentAsBytes.toString());

        if (attempted_assignment.num_evaluated < total_teachers) {
            console.log("Enough teachers haven't checked the assignment yet")
            throw new Error("Enough teachers haven't checked the assignment yet");
        }

        // don't show registration $HELLO$ records
        if (attempted_assignment.assignment_content === "$HELLO$") {
            throw new Error(`${attempted_assignment} does not exist`);
        }

        // no need to show these fields anyway
        delete attempted_assignment.scores;
        delete attempted_assignment.num_evaluated;
        delete attempted_assignment.userID;


        console.log(attempted_assignment);
        console.info('============= END : queryAssignment ===========');
        return JSON.stringify(attempted_assignment);
    }


    async queryAllAssignments(ctx) {
        console.info('============= START : queryAllAssignments ===========');

        let cid = new ClientIdentity(ctx.stub);
        let tempUserID = cid.getID();

        const startKey = '0';
        const endKey = '99999';

        const iterator = await ctx.stub.getStateByRange(startKey, endKey);

        const allResults = [];
        while (true) {
            const res = await iterator.next();

            if (res.value && res.value.value.toString()) {
                // console.log(res.value.value.toString('utf8'));

                const Key = res.value.key;
                let assignment_attempted;
                try {
                    assignment_attempted = JSON.parse(res.value.value.toString('utf8'));

                    // don't show registration $HELLO$ records or other students assignments or assignments where grading has not been finished yet
                    if (assignment_attempted.assignment_content === "$HELLO$" || assignment_attempted.userID != tempUserID || assignment_attempted.num_evaluated < total_teachers) {
                        continue;
                    }

                    // no need to show these fields anyway
                    delete assignment_attempted.scores;
                    delete assignment_attempted.num_evaluated;
                    delete assignment_attempted.userID;


                } catch (err) {
                    console.log(err);
                    assignment_attempted = res.value.value.toString('utf8');
                }

                allResults.push(assignment_attempted);
            }
            if (res.done) {
                await iterator.close();
                console.log(allResults.length);
                if (allResults.length === 0) {
                    console.log("Enough teachers haven't checked the assignment yet")
                    throw new Error("Enough teachers haven't checked the assignment yet");
                }
                console.info(allResults);
                console.info('============= END : queryAllAssignments ===========');
                return JSON.stringify(allResults);
            }
            console.log("===================================")
        }
    }

    async teacherQueryUngraded(ctx){
        console.info('============= START : teacherQueryUngraded ===========');

        let cid = new ClientIdentity(ctx.stub);
        let teacher_ID = cid.getID();

        const startKey = '0';
        const endKey = '99999';

        const iterator = await ctx.stub.getStateByRange(startKey, endKey);

        const allResults = [];
        while (true) {
            const res = await iterator.next();

            if (res.value && res.value.value.toString()) {
                // console.log(res.value.value.toString('utf8'));

                const Key = res.value.key;
                let assignment_attempted;
                try {
                    assignment_attempted = JSON.parse(res.value.value.toString('utf8'));

                    // don't show registration $HELLO$ records or assignments which this teacher has already graded
                    if (assignment_attempted.assignment_content === "$HELLO$" || teacher_ID in assignment_attempted.scores) {
                        continue;
                    }
                    
                    // Essentially just show userID, assignment_id and assignment_content
                    delete assignment_attempted.final_score;
                    delete assignment_attempted.scores;                    
                    delete assignment_attempted.num_evaluated;
                    delete assignment_attempted.range_of_scores;
                    delete assignment_attempted.high_deviation;
                    

                } catch (err) {
                    console.log(err);
                    assignment_attempted = res.value.value.toString('utf8');
                }

                allResults.push(assignment_attempted);
            }
            if (res.done) {
                await iterator.close();
                console.log(allResults.length);
                if (allResults.length === 0) {
                    console.log("No remanining assignments to evaluate right now")
                    throw new Error("No remanining assignments to evaluate right now");
                }
                console.info(allResults);
                console.info('============= END : teacherQueryUngraded ===========');
                return JSON.stringify(allResults);
            }
        }
    }

    async submitScore(ctx, student_id, assignment_id, marks){
        console.info('============= START : submitScore ===========');
        
        let cid = new ClientIdentity(ctx.stub);
        let teacher_ID = cid.getID();

        let combination_id;
        combination_id = (assignment_id.toString()).concat("-", (student_id.toString()));

        // get the attempted_assignment from chaincode state
        const attempted_assignmentAsBytes = await ctx.stub.getState(combination_id);
            if (!(attempted_assignmentAsBytes) || attempted_assignmentAsBytes.length === 0) {
                throw new Error(`${combination_id} does not exist`);
            }
        const attempted_assignment = JSON.parse(attempted_assignmentAsBytes.toString());

        // Score can only be submitted if the teacher hasn't already submitted the score before
        if (!(teacher_ID in attempted_assignment.scores)) {
            attempted_assignment.scores[teacher_ID] = marks;
            attempted_assignment.num_evaluated += 1;

            if (attempted_assignment.num_evaluated == total_teachers) {
                let scores_list;
                scores_list = Object.values(attempted_assignment.scores);
                let scores_list_int;
                scores_list_int = scores_list.map(Number);
                scores_list_int.sort(function(a,b) {return a - b;});
                let max = scores_list_int[scores_list.length-1];
                let min = scores_list_int[0];
                attempted_assignment.range_of_scores = max - min;
                attempted_assignment.final_score = scores_list_int[2];
                
                if (attempted_assignment.range_of_scores > 10) {
                    attempted_assignment.high_deviation = true;
                } else {
                    attempted_assignment.high_deviation = false;
                }
            }
        } else {
            console.log("Teacher has already graded this assignment for this student!`")
            throw new Error(`Teacher has already graded this assignment for this student!`);
        } 
        
        await ctx.stub.putState(combination_id, Buffer.from(JSON.stringify(attempted_assignment)));
            console.info('============= END : submitScore ===========');
        }
}

module.exports = GradeNewScope;
