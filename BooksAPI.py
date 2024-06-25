from flask import Flask, request, jsonify
from services import book_service,book_functions,user_functions,user_service
import json
import cachetools
from cachetools import TTLCache
import copy
from datetime import datetime


app = Flask(__name__)
books = book_service.Books() 
users = user_service.Users()  
cache = TTLCache(maxsize=100, ttl=900)
cache['not_expired'] = True

#the home page
@app.route("/")
def home(): 
    return "Welcome to BookStoreAPI"

#endpoint for creating a new user
@app.route("/api/user/register",methods=["POST"])
def registerUser():
    book_functions.log("request recieved on /api/user/register")
    body = request.json   
    if not user_functions.check_params_add(body):
        return {"status": 400 , "message":"Missing parameters" }
    if users.add_user(body):
        firstname = body["firstname"]
        lastname = body['lastname']
        book_functions.log("User {firstname} {lastname} was added to the db ")
        return {"status": "201" , "message": "User Succesfully added"}
    else:
        return {"status": "404" , "message": "There was an error adding the User"}

#endpoint for adding a book
@app.route("/api/add/<user_id>",methods=["POST"])
def addBook(user_id):
    book_functions.log("request recieved on /api/add/{user_id}")
    if not users.check_user_exists(user_id):
        return {"status": 400 , "message":"User doesn't exist" }
    body = request.json   
    if not book_functions.check_params_add(body):
        return {"status": 400 , "message":"Missing parameters" }
    if books.add_book(body): 
        book_functions.log(f"A book was added to the db by {user_id} ")
        title = body["title"]
        users.add_log(f"A book with title {title} was added to the db by User {user_id} ")
        return {"status": "201" , "message": "Book Succesfully added"}
    else:
        return {"status": "404" , "message": "There was an error adding the book"}

#endpoint for getting a book 
@app.route("/api/get/book/<book_id>",methods=["GET"])
def getBook(book_id):
    book_functions.log(f"request recieved on /api/get/{book_id}")
    json_cache = "bookcache.json"
    data = book_functions.fetch_data(cache=cache,json_cache=json_cache,method="GET",book_id=book_id,category=None)
    
    return data

@app.route("/api/get/category/<category>",methods=["GET"])
def getCategory(category):
    book_functions.log(f"request recieved on /api/get/category/{category}")
    json_cache = "bookcache.json"
    data = book_functions.fetch_data(cache=cache,json_cache=json_cache,method="GET",book_id=None,category=category)
    return data


#endpoint for deleting a book
@app.route("/api/delete/<book_id>/<user_id>",methods=["DELETE"])
def deleteBook(book_id,user_id):
    book_functions.log(f"request recieved on /api/delete/{book_id}/{user_id}")
    if not users.check_user_exists(user_id):
        return {"status": 400 , "message":"User doesn't exist" }
    #if the  deleted bookid is present in cache we remove it from cache
    try:
        with open("bookcache.json","r") as file:
            json_data = json.load(file)
    except Exception:
        json_data = None
    if json_data is not None:
        book_functions.remove_from_cache(book_id,json_data)
    if books.delete_book(book_id):
        book_functions.log(f"Book with id: {book_id} was removed from the db")
        users.add_log(f"The book with id {book_id} was removed from the db by User {user_id} ")
        return {"status": "200", "message": "Book Succesfully deleted"}
    else:
        return {"status": "404" , "message": "There was an error deleting the book"}
    



#endpoint for updating a book   
@app.route("/api/update/<book_id>/<user_id>",methods=["PUT"])
def updateBook(book_id,user_id):
    book_functions.log(f"request recieved on /api/update/{book_id}")
    if not users.check_user_exists(user_id):
        return {"status": 400 , "message":"User doesn't exist" }
    body = request.json 
    if not book_functions.check_params_add(body):
        return {"status": 400 , "message":"Missing parameters" }
    try:
        with open("bookcache.json","r") as file:
            json_data = json.load(file)
    except Exception:
        json_data = None
    if json_data is not None:
        book_functions.update_in_cache(book_id,json_data,body["title"],body["author"],body["price"],body["category"])
    if books.update_book(book_id,body["title"],body["author"],body["price"],body["category"]):
        book_functions.log(f"Book with id: {book_id} was updated in the db")
        title = body["title"]
        users.add_log(f"A book with title {title} was modified in the db by User {user_id} ")
        return {"status": "200", "message": "Book Succesfully updated"}
    else:
        return {"status": "404" , "message": "There was an error updating the book"}

if __name__ == "__main__":

    app.run(debug = True)
    


    