import requests
import json
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn


app = FastAPI()

from mbbank import MBBANK

mbbank = MBBANK()


class LoginDetails(BaseModel):
    username: str
    password: str
    account_number: str
@app.post('/login', tags=["login"])
def login_api(input: LoginDetails):
        result = mbbank.handleLogin(input.username, input.password)
        return json.loads(result)

@app.post('/get_balance', tags=["get_balance"])
def get_balance_api(input: LoginDetails):
        session_raw = mbbank.handleLogin(input.username, input.password)
        balance = mbbank.get_balance(json.loads(session_raw),input.account_number)
        return json.loads(balance)
    
class Transactions(BaseModel):
    username: str
    password: str
    account_number: str
    from_date: str
    to_date: str
    
@app.post('/get_transactions', tags=["get_transactions"])
def get_transactions_api(input: Transactions):
        session_raw = mbbank.handleLogin(input.username, input.password)
        history = mbbank.getTransactionHistory(input.from_date,input.to_date,json.loads(session_raw))
        return json.loads(history)


if __name__ == "__main__":
    uvicorn.run(app ,host='0.0.0.0', port=3000)


