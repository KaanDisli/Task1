from flask import Flask, request, jsonify
import psycopg2
class Books:

    def __init__(self) -> None:
        self.conn = psycopg2.connect(host="localhost",dbname="postgres", user="postgres", password="kaan2002", port=5432)
        self.cur = self.conn.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS books (
                    id INT PRIMARY KEY,
                    title VARCHAR(255),
                    author VARCHAR(255),
                    price INT,
                    category VARCHAR(255),
                    serialNumber VARCHAR(255) UNIQUE
                    );
""")
        self.conn.commit()
        self.highest_id = self.highest_id()

    def highest_id(self):
        self.cur.execute("""
        SELECT MAX(id) FROM books 
                         """)
        query_result = self.cur.fetchone()
        if query_result == (None,):
            return 0
        return query_result[0]

    def add_book(self,body):
        try:
            print(body)
            print(self.highest_id)
            self.highest_id = self.highest_id + 1
            self.cur.execute("INSERT into books (id,title,author,price,category,serialNumber) VALUES(%s,%s,%s,%s,%s,%s)", (self.highest_id,body["title"],body["author"],body["price"],body["category"],body["serialNumber"]) )
            self.conn.commit()
        except Exception as e:
            print("There was an error inserting the book: ", e)
            if self.conn is not None:
                self.conn.rollback()
            return False
        return True
    
    def get_book(self,book_id):
        ###MAKE SURE TO PREVENT SQL INJECTION
        try:
            self.cur.execute("SELECT * FROM books WHERE books.id = %s",book_id)
            query_result = self.cur.fetchone()
            if query_result == None:
                return -1
            data = {"id" : query_result[0],
                    "title": query_result[1],
                    "author": query_result[2],
                    "price": query_result[3],
                    "category":query_result[4],
                    "serialNumber":query_result[5]

            }
        except Exception as e:
            print("There was an error querying the book: ", e)
            return False
        return data
    
    def get_all_books(self):
        ###MAKE SURE TO PREVENT SQL INJECTION
        try:
            self.cur.execute("SELECT * FROM books")
            query_result = self.cur.fetchall()
            if query_result == None:
                return -1

        except Exception as e:
            print("There was an error querying the book: ", e)
            return False
        return query_result
    
    def delete_book(self,book_id):
        try:
            self.cur.execute("DELETE FROM books WHERE books.id = (%s)",(book_id,))
            affected_rows = self.cur.rowcount
            self.conn.commit()
        except Exception as e: 
            print("There was an error deleting the book: ", e)
            return False
        if affected_rows != 1:
            print("Book does not exist")
            return False
        return True
    
    def update_book(self,book_id,body):
        for e in body:
            key=e
            value = body[key]
        
        print("we arrived at update_book")
        try:
            self.cur.execute(f"UPDATE books SET {key} = {value} WHERE books.id = {book_id}")
            affected_rows = self.cur.rowcount
            self.conn.commit()
            
        except Exception as e: 
            print("There was an error updating the book: ", e)
            return False
        if affected_rows != 1:
            print("Book does not exist")
            return False
        return True

