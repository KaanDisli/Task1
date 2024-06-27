from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime
class Users:
    def __init__(self) -> None:
        self.conn = psycopg2.connect(host="localhost",dbname="postgres", user="postgres", password="kaan2002", port=5432)
        self.cur = self.conn.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY,
                    firstname VARCHAR(255),
                    lastname VARCHAR(255),
                    password INT,
                    Gender CHAR
                    );
""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS auditlogs (
                    
                    log VARCHAR(255)

                    );
""")
        self.conn.commit()
        self.highest_id = self.highest_id()

    def add_log(self,message):
        current_time = datetime.now().time()
        message = f'{message} : at time {current_time}'
        self.cur.execute("INSERT into auditlogs (log) VALUES(%s)", (message,) )
        self.conn.commit()

    def highest_id(self):
        self.cur.execute("""
        SELECT MAX(id) FROM users 
                         """)
        query_result = self.cur.fetchone()
        if query_result == (None,):
            return 0
        return query_result[0]
    
    def add_user(self,body):
        try:
            firstname = body["firstname"]
            lastname = body["lastname"]
            self.highest_id = self.highest_id + 1
            self.cur.execute("INSERT into users (id,firstname,lastname,password,gender) VALUES(%s,%s,%s,%s,%s)", (self.highest_id,body["firstname"],body["lastname"],body["password"],body["gender"]) )
            self.conn.commit()
        except Exception as e:
            print("There was an error creating the user: ", e)
            return False
        self.add_log(f"User with name {firstname} and lastname {lastname} was created")
        return True

    def check_user_exists(self,user_id):
        self.cur.execute("""
        SELECT * FROM users WHERE id = (%s)
                         """, (user_id,))
        query_result = self.cur.fetchone()
        if query_result == None:
            return False
        return True
    