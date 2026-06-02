<!-- This is markdown -->

# The flow/goal of my Expense Tracker CLI application 





****GOAL**** - **I am building a command-line program where a user can:**

Record income  
Record expenses  
View transactions  
Check current balance  
Generate monthly reports  

***
       
**What i would be using:**  
SQLite (as database )   
Python functions  
Classes and OOP  
SQL queries  
Data structures  
Error handling  
Project organization  
Reporting and aggregation  

Start by creating a Transaction Class

N/B: Every income or expense is a transaction.


***

**Transaction attributes are:**  
amount  
category  
description    
date  
type
     
****
**Files i should have :**  
main.py  
models.py  
database.py  
services.py  
reports.py


**In main.py;**

Display:

1. Add Income
2. Add Expense
3. View Transactions
4. Check Balance
5. Exit


**Flow:**

User Selects Option  
        ↓  
Program Executes Function  
        ↓  
Returns To Menu 

Keep looping until the user chooses Exit.  


**Create a function:**

calculate_balance() 

  ***

**Add SQLite Database**


Create:

expenses.db

**Table:**

transactions

**Columns:**

id  
amount  
category  
description  
type  
date

**Database Flow**  
User Adds Expense  
        ↓  
Python Function  
        ↓  
INSERT INTO transactions  
        ↓  
SQLite Stores Record  


**Create Database Functions**

In database.py

**Functions:**

create_table()  
add_transaction()  
get_transactions()  
delete_transaction()

**N/B:**  Each function should do only one job.

**Store category with each transaction.**  
Example:

Expense  
Amount: 5000  
Category: Food  
Description: Restaurant

**Monthly Reports**


Example:

**June 2026 Report**

Income:
50000

Expenses:  
Food: 5000  
Transport: 3000  
Shopping: 10000  

Total Expenses:
18000

Balance:
32000

**Flow:**

Get Transactions  
       ↓  
Filter By Month  
       ↓  
Calculate Totals  
       ↓  

**Display Report**  
Search Transactions

Examples:

Search by category  
Search by date  
Search by type  

**User:**

Enter category: Food

**Output:**

Food Expenses

Restaurant 5000  
Snacks 1000  

**Delete Transactions**

Menu:

Delete Transaction

Flow:

View Transactions  
    ↓  
Select ID  
       ↓  
Delete Record  

**SQL :**

DELETE FROM transactions  
WHERE id = ?
    
***

**Export to CSV**  
Generate:
transactions.csv

Example:

id,date,type,amount,category  
1,2026-06-01,income,50000,Salary  
2,2026-06-01,expense,2000,Food  

**Useful library:**
csv

**Error Handling**

Handle cases like:

Amount must be greater than zero.  
Transaction ID not found.  
Invalid menu option.
Never let the program crash because of user input.
