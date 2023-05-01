# Greystone Mortgages
This application is designed to provide basic CRUD functionality around mortgages.

## Installation
Inside a python or a virtual environment execute: `pip install -r requirements.txt`

## Execution
In the project root directory execute: `uvicorn app.main:app --reload`

## Endpoint Description

### health_check
Executes a basic DB query to ensure the health of the service. Should return 200/Status:Ok if the service is functional.