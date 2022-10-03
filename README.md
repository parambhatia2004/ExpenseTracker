# ExpenseTracker
Users can register, log in.
All users belong to the same household.
Users can raise bills for others to pay.
The status of payees is displayed to only the payer( the person who raised the bill)
When registering, the email is verified to be of email type, the username has to be 5 letters minimum, and cannot be an existing username.
The password is minimum 8 characters, and is hashed.

When setting a bill, users can choose who to assign the bill to, along with a bill name.
Any payees who log in after the bill has been assigned will get a flash notification of how much to pay to whom.

In order to settle a bill, the payee will first confirm that they have paid.
This will send a message to the user who raised the bill, and ask them to confirm if they have received a payment from said user
This is an extra feature as it allows for data to be check from both ends, and the user cannot just say they paid it without confirmation.

Once this is settled, the payee status will be updated.

Another design decision is that the bill does not get automatically deleted, since the user may want to keep record of it for budgeting.

Another main feature is being able to split the bill between only a part of the household, and this is a very beneficial use.

The application uses Ajax frequently in order to get server-side data and increases usability.

No bootstrap is used.
