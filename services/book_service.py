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
        self.conn.commit()

    def add_book(self,body):
        try:
            print("body")
            print(body)
            self.cur.execute("INSERT into books (id,title,author,price) VALUES(%s,%s,%s,%s)", (body["id"],body["title"],body["author"],body["price"]) )
            self.conn.commit()
        except Exception as e:
            print("There was an error inserting the book: ", e)

            return False
        #self.conn.close()
        #self.cur.close()
        finally:
            self.conn.close()
            self.cur.close()
        return True
    
    def get_book(self,book_id):

        ###MAKE SURE TO PREVENT SQL INJECTION
        
        try:
            self.cur.execute("SELECT * FROM books WHERE books.id = %s",book_id)
            query_result = self.cur.fetchone()
            if query_result == None:
                return -1
            print("query_result")
            print(query_result)
            data = {"id" : query_result[0],
                    "title": query_result[1],
                    "author": query_result[2],
                    "price": query_result[3],

            }
        except Exception as e:
            print("There was an error querying the book: ", e)
            return False

        #self.conn.close()
        #self.cur.close()
        return data
