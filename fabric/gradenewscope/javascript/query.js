/*
 * SPDX-License-Identifier: Apache-2.0
 */

'use strict';

const {FileSystemWallet, Gateway} = require('fabric-network');
const fs = require('fs');
const path = require('path');

const ccpPath = path.resolve(__dirname, '..', '..', 'basic-network', 'connection.json');
const ccpJSON = fs.readFileSync(ccpPath, 'utf8');
const ccp = JSON.parse(ccpJSON);
let choice, user, assignment_id;

process.argv.forEach(function (val, index, array) {
    choice = array[2];
    user = array[3];
    assignment_id = array[4]
});

async function main() {
    try {
        // Create a new file system based wallet for managing identities.
        const walletPath = path.join(process.cwd(), 'wallet');
        const wallet = new FileSystemWallet(walletPath);
        console.log(`Wallet path: ${walletPath}`);

        // Check to see if we've already enrolled the user.
        const userExists = await wallet.exists(user);
        if (!userExists) {
            console.log(`An identity for the user ${user} does not exist in the wallet`);
            console.log('Run the registerUser.js application before retrying');
            return;
        }

        // Create a new gateway for connecting to our peer node.
        const gateway = new Gateway();
        await gateway.connect(ccp, {wallet, identity: user, discovery: {enabled: false}});

        // Get the network (channel) our contract is deployed to.
        const network = await gateway.getNetwork('mychannel');

        // Get the contract from the network.
        const contract = network.getContract('gradenewscope');

        if (choice === 'queryAssignment') {
            console.log("hello");
            const result = await contract.evaluateTransaction('queryAssignment', assignment_id);
            console.log(`Result is: ${result.toString()}`);
        } else if (choice === 'queryAllAssignments') {
            const result = await contract.evaluateTransaction('queryAllAssignments');
            console.log(`Result is: ${result.toString()}`);
        } else if (choice === 'teacherQueryUngraded') {
            const result = await contract.evaluateTransaction('teacherQueryUngraded');
            console.log(`Result is: ${result.toString()}`);
        } else {
            console.log(`Choice ${choice} not valid`);  
        }

    } catch (error) {
        console.error(`Failed to evaluate transaction: ${error}`);
        process.exit(1);
    }
}

main();
