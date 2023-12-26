# loan_amortization_app

This loan amortization app contains the endpoints listed below. The endpoints are presented as curl commands with sample input and output values.

**Create user** (not authenticated):

curl -X POST "http://localhost:8000/users/" -H "Content-Type: application/json" -d '{
    "email": "user@example.com",
    "password": "pw",
    "first_name": "First",
    "last_name": "Last"
}'

Sending password in plaintext to API is not secure and is only done here for app + authentication demo purposes. The authentication done in this API is very basic and not how it would be done if the app was in use. For example, the "login" which is done by sending username (email) and password with every endpoint is not stored to keep a user logged in. Furthermore, when creating a user the password is not properly hashed as it would be done if this app was in use.

**Create loan:**

curl -X POST -u <email>:<password> "http://localhost:8000/users/{user_id}/loans" -H "Content-Type: application/json" -d '{
    "amount": 1000000,
    "annual_interest_rate": 5,
    "loan_term": 360,
    "type": "conventional"
}'

**Get user’s loans:**

curl -X GET -u <email>:<password> "http://localhost:8000/users/{user_id}/loans"

Sample output (shows user's loans and loans shared with user):

{"user's loans: ":[{"loan_term":360,"id":4,"user_id":3,"amount":1000000.0,"annual_interest_rate":1.0,"type":"conventional"}],"loans shared with user: ":[{"loan_term":360,"id":1,"user_id":2,"amount":1000000.0,"annual_interest_rate":7.0,"type":"conventional"}]}

**Get loan schedule:**

curl -X GET -u <email>:<password> "http://localhost:8000/users/{user_id}/loans/{loan_id}/schedule"

The loan schedule endpoint shows a list of dictionaries containing each month's loan information. The monthly payment is the same every month and is the sum of the principal and interest payments. These values can also be seen separately by selecting the 'Interest' and 'Principal' columns from the dataframe as indicated in a comment in the function *get_loan_schedule* in file controller.py. The remaining balance is the remaining principal balance as is the typical value presented in amortization calculators.

Sample output (12 month loan):

output based on this loan: {"loan_term":12,"id":5,"user_id":2,"annual_interest_rate":3.0,"amount":75000.0,"type":"conventional"}

[{"Month":1.0,"Remaining balance":68835.47,"Monthly payment":6352.03},{"Month":2.0,"Remaining balance":62655.53,"Monthly payment":6352.03},{"Month":3.0,"Remaining balance":56460.15,"Monthly payment":6352.03},{"Month":4.0,"Remaining balance":50249.27,"Monthly payment":6352.03},{"Month":5.0,"Remaining balance":44022.86,"Monthly payment":6352.03},{"Month":6.0,"Remaining balance":37780.89,"Monthly payment":6352.03},{"Month":7.0,"Remaining balance":31523.32,"Monthly payment":6352.03},{"Month":8.0,"Remaining balance":25250.1,"Monthly payment":6352.03},{"Month":9.0,"Remaining balance":18961.2,"Monthly payment":6352.03},{"Month":10.0,"Remaining balance":12656.57,"Monthly payment":6352.03},{"Month":11.0,"Remaining balance":6336.19,"Monthly payment":6352.03},{"Month":12.0,"Remaining balance":-0.0,"Monthly payment":6352.03}]

**Get loan summary:**

curl -X GET -u <email>:<password> "http://localhost:8000/users/{user_id}/loans/{loan_id}/summary/{month_num}"

Sample output (based on loan from above example)

Month 1:

{"Current principal balance":68835.47,"Total principal paid":6164.53,"Total interest paid":187.5}

Month 10:

{"Current principal balance":12656.57,"Total principal paid":62343.43,"Total interest paid":1176.85}

Month 12:

{"Current principal balance":-0.0,"Total principal paid":75000.01,"Total interest paid":1224.33}

**Share loan:**

curl -X POST -u <email>:<password> "http://localhost:8000/users/{user_id}/loans/{loan_id}/share" -H "Content-Type: application/json" -d '{
    "user_email": "existing_user@example.com"
}'

For the purpose of this exercise sharing a loan (as implemented in the share loan endpoint) refers to adding the user with the given email to a table in the database that links the loan_id with that user's user_id. When that user views their loans they will be able to see the loan shared with them. When accessing the loan schedule or loan summary endpoints they will have access to see the information for the loan that was shared with them. However, they will not have permission to share this loan with others since they are not the primary owner of the loan. If the user's email does not exist in the database, an error is thrown. In a future iteration the user could be invited to the app or the details of the loan could be sent in an email to that person.

A user that has type = 'broker' has access to create a loan for a user and view the loans of any user. They do not have permission to share a loan for a user. This functionality can be updated or removed depending on how stakeholders want to handle access of brokers or other employees of the institutions involved in obtaining the loan.

**Future Steps**

Adding tests for the endpoints and methods is an important next step.
Another step would be adding dates to the loan information rather than having month numbers from 1 to loan_term.
For a larger project the functions related to similar entities or actions would be broken up into different files rather than have all endpoints stored in main.py and most functions in controller.py.

**Sources**

I used the amortization calculator [here](https://www.bankrate.com/mortgages/amortization-calculator/)
and the explanation of the math [here](https://www.ramseysolutions.com/real-estate/amortization-schedule#:~:text=To%20calculate%20amortization%2C%20first%20multiply,toward%20principal%20for%20that%20month.) to learn how amortization calculations are done.
