import psycopg2 
from fastapi import FastAPI
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
import requests
import json
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import logging

WEBHOOK_URL="http://127.0.0.1:5678/webhook-test/30f43367-8e70-419c-9873-144b9d8a3aba"





logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='app.log',
    filemode='a'
)

connection=psycopg2.connect(
    host='localhost',
    database='helpdesk_db',
    user='postgres',
    password='admin123'
)
app= FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class Help_Desk(BaseModel):
    customer_name:str
    email:str
    subject:str
    message:str
@app.post("/new_query")
def insert_data(user_data: Help_Desk):
    cursor=connection.cursor()
    insert_data="INSERT INTO tickets(customer_name,email,subject,message) VALUES (%s,%s,%s,%s) RETURNING id;"
    cursor.execute(insert_data,(user_data.customer_name,user_data.email,user_data.subject,user_data.message))
    ticket_id=cursor.fetchone()[0]
    connection.commit()
    cursor.close()
    logging.info(f"Customer {user_data.customer_name} added to the database")
    n8n_payload={
        "ticket_id":ticket_id,
        "customer_name":user_data.customer_name,
        "email":user_data.email,
        "subject":user_data.subject,
        "message":user_data.message
    }
    try:
        requests.post(WEBHOOK_URL,json=n8n_payload,timeout=3)
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to trigger n8n for ticket {ticket_id}: {e}")
    return {
        "message": "Ticket created successfully",
        "ticket_id": ticket_id
    }