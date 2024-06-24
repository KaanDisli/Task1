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
       # print("TEST 1")
        #print("Creating Local cache ")
        if method == "GET":
            #print("TEST 2")
            json_data = books.get_book(book_id)
            if json_data == -1: 
                return {"status": 403, "message":"Book does not exist"}
            #print("TEST 3")

            #print("TEST 4")
            with open(json_cache,"w") as file:
               # print("TEST 5")
                json.dump(json_data,file)
    #print("TEST 6")            
    return json_data


@app.route("/")
def home(): 
    return "Welcome to BookStoreAPI"

@app.route("/api/add",methods=["POST"])
def addBook():
    global status 
    status = True
    print("TEST 9")
    body = request.json
    print("TEST 10")
    if books.add_book(body):
        print("TEST 11")
        return {"message": "Book Succesfully added"}
    else:
        print("TEST 12")
        return {"message": "There was an error adding the book"}


@app.route("/api/get/<book_id>",methods=["GET"])
def getBook(book_id):
    #print("TEST 7")
    global status
    json_cache = "bookcache.json"
    data = fetch_data(update=True,json_cache=json_cache,method="GET",book_id=book_id)
    
    status = False
    #print("TEST 8")
    return data



if __name__ == "__main__":

    app.run(debug = True)
    