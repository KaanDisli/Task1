from flask import Flask, request, jsonify
from services import book_service
import json

app = Flask(__name__)
books = book_service.Books()  
status = True
def fetch_data(*, update: bool = False, json_cache, method: bool = "GET",book_id):
    if update: 
        json_data = None  
    else:
        try:
            with open(json_cache,"r") as file:
                json_data = json.load(file)
                print("Fetched data from local cache")
        except(FileNotFoundError,json.JSONDecodeError) as e:
            print(f'Problem with local cache:  {e}')
            json_data = None 

    if json_data == None:
        print("Creating Local cache ")
        if method == "GET":
            json_data = books.get_book(book_id)
            if json_data == -1: 
                return {status: 403, "message":"Book does not exist"}
            with open(json_cache,"w") as file: 
                json.dump(json_data,file)
         
    return json_data


@app.route("/")
def home(): 
    return "Welcome to BookStoreAPI"

@app.route("/api/add",methods=["POST"])
def addBook():
    global status 
    status = True
    body = request.json   
    if books.add_book(body): 
        return {"status": "201" , "message": "Book Succesfully added"}
    else:
        return {"status": "404" , "message": "There was an error adding the book"}




@app.route("/api/get/<book_id>",methods=["GET"])
def getBook(book_id):

    global status
    json_cache = "bookcache.json"
    data = fetch_data(update=True,json_cache=json_cache,method="GET",book_id=book_id)
    
    status = False

    return data

@app.route("/api/delete/<book_id>",methods=["DELETE"])
def deleteBook(book_id):
    if books.delete_book(book_id):
        return {"status": "200", "message": "Book Succesfully deleted"}
    else:
        return {"status": "404" , "message": "There was an error deleting the book"}

if __name__ == "__main__":

    app.run(debug = True)
    


    