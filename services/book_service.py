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
                    price INT
                    );
""")
        with open('bookcache.json', 'w') as f:
            pass 
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
            self.cur.execute("INSERT into books (id,title,author,price) VALUES(%s,%s,%s,%s)", (self.highest_id,body["title"],body["author"],body["price"]) )
            self.conn.commit()
        except Exception as e:
            print("There was an error inserting the book: ", e)
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
            print("query_result")
            print(query_result)
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
    
    def update_book(self,book_id,title,author,price):
        try:
            self.cur.execute("UPDATE books SET title = (%s), author = (%s), price = (%s) WHERE books.id = (%s)",(title,author,price,book_id,))
            affected_rows = self.cur.rowcount
            self.conn.commit()
        except Exception as e: 
            print("There was an error updating the book: ", e)
            return False
        if affected_rows != 1:
            print("Book does not exist")
            return False
        return True

