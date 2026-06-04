<!-- This is markdown -->

# The flow/goal of my Expense Tracker Backend (API VERSION)





****GOAL**** - **I am building a fastapi application where a user can:**

Record income  
Record expenses  
View transactions  
Check current balance  
Generate monthly reports  

***
       
**What i would be using:**  
SQLite (as database )    
SQLAlchemy queries  
Data structures  
Error handling  
Project organization  
Reporting and aggregation  


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
schema.py  
reports.py

***

**In main.py;**

You should have your:
 
Routes of different endpoints  
HTTP REQUESTS   
App running  
Defination of a response model 

**Flow:**

Client (Frontend)  
        ↓  
HTTP Request (GET / POST / DELETE)  
        ↓  
FastAPI Endpoint (main.py)  
        ↓  
Schema Validation (schemas.py)  
        ↓  
Service Layer (services.py)      
        ↓  
Database Layer (database.py)  
        ↓  
SQLite Database (transactions table)    
        ↓    
Return Data / JSON Response  
        ↓  
Client Receives Response    

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

***

**Add Income / Expense**

User sends POST /transactions  
        ↓  
FastAPI receives request (main.py)   
        ↓  
Validate input (schemas.py)  
        ↓  
Send data to database.py  
        ↓  
INSERT INTO transactions  
        ↓  
SQLite stores record  
        ↓  
Return: "Transaction added successfully"   

***

**View All Transactions**  
User sends GET /transactions  
        ↓  
main.py endpoint triggered  
        ↓  
database.py fetches all records  
        ↓   
Return list of transactions  
        ↓  
Client displays JSON data  

***

**Check Balance**  
User sends GET /balance  
        ↓    
main.py endpoint triggered   
        ↓  
database.py fetches all transactions  
        ↓  
services.py calculates:  
        income - expenses  
        ↓  
Return balance JSON  

***

**Monthly Report**  
User sends GET /reports/monthly?month=2026-06  
        ↓  
main.py receives request   
        ↓  
database.py returns all transactions   
        ↓  
services.py filters by month  
        ↓  
reports.py aggregates:  
        income, expenses, categories  
        ↓  
Return structured report JSON  

***

**Search Transactions**  
User sends GET /transactions/search?category=Food  
        ↓  
main.py receives request  
        ↓   
database.py fetches matching records  
        ↓  
Return filtered transactions  
        ↓  
Client sees results  

***

**Delete Transaction**  
User sends DELETE /transactions/{id}    
        ↓    
main.py endpoint triggered    
        ↓    
database.py runs:  
DELETE FROM transactions WHERE id = ?  
        ↓  
SQLite removes record  
        ↓  
Return success message  


***

**Export to CSV**  
User sends GET /export/csv  
        ↓ 
main.py endpoint triggered  
        ↓  
database.py fetches all transactions  
        ↓  
services.py formats data  
        ↓  
csv module writes file (transactions.csv)  
        ↓  
Return download response / file path  


***



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

