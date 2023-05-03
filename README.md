# Greystone Mortgages
This application is designed to provide basic CRUD functionality around mortgages.

## Prerequisites
Python 3.10+

## Installation
Inside a python or a virtual environment execute: `pip install -r requirements.txt`

## Execution
In the project root directory execute: `uvicorn app.main:app --reload`

## Endpoint Description

### health_check
Executes a basic DB query to ensure the health of the service. Should return 200/Status:Ok if the service is functional.

### /users/
User related endpoints (currently create only)

### /users/{email}/loans/
Retrieve loans belonging to a given user identified by email

### /loans/{email}/
Create loan for an existing user

### /loans/{id}/schedule/
Retrieve a payout schedule for a given loan

### /loans/{id}/month/{month}/
Retrieve a summary for a given month of a loan

### /loans/{id}/share/{email}/
Associates a loan with a given user