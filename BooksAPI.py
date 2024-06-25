from flask import Flask, request, jsonify
from services import book_service
import json
import cachetools
from cachetools import TTLCache
import copy

app = Flask(__name__)
books = book_service.Books()  
cache = TTLCache(maxsize=100, ttl=900)
cache['not_expired'] = True


#we remove the book with the id passed as parameter from the cache
def remove_from_cache(id,list):
    duplicate_list = copy.deepcopy(list)
    id = int(id)
    for elem in list:
        id_, title, author, price = elem
        if id_ == id:   
            duplicate_list.remove(elem)
            json_data = duplicate_list
            with open("bookcache.json","w") as file:
                json.dump(json_data,file)
            return True
                
    return False

#Here we iterate over the books in the cache to see if the book with the id passed as a parameter exists
def search_id_list(id,list):
    
    id = int(id)
    for elem in list:
        id_, title, author, price = elem
        if id_ == id:   
            return True, {
                "id":id,"title":title,"author":author,"price":price
            }
    return False, {"status": 403, "message":"Book does not exist"}



def fetch_data(*,cache,json_cache, method: bool = "GET",book_id):
    #if the cache has expired we need to make a db query for the json data
    if cache['not_expired'] != True: 
        json_data = None  
    else:
        try:
            #if the cache has not expired we open the local cache
            with open(json_cache,"r") as file:
                json_data = json.load(file)
                print("Fetched data from local cache")
                #if the book can be found in the local cache we return it, if not we expire the timer on the cache make a db query
                status, message =  search_id_list(book_id,json_data) 
                if status:
                    return message
                else:
                    cache.clear()
                    json_data = None
        except(FileNotFoundError,json.JSONDecodeError) as e:
            print(f'Problem with local cache:  {e}')
            json_data = None 

    if json_data == None:
        print("Creating Local cache ")
        if method == "GET":
            #we make the db query here
            json_data = books.get_all_books()                
            with open(json_cache,"w") as file: 
                #we need to set the cache timer again now that we have gotten the new data
                cache['not_expired'] = True
                #we write the new data into our local cache
                json.dump(json_data,file)
    #after making our query and writing it in the local cache we return if it is present as a book or not    
    status, message =  search_id_list(book_id,json_data) 
    return message

#the home page
@app.route("/")
def home(): 
    return "Welcome to BookStoreAPI"

#endpoint for adding a book
@app.route("/api/add",methods=["POST"])
def addBook():
    body = request.json   
    if books.add_book(body): 
        return {"status": "201" , "message": "Book Succesfully added"}
    else:
        return {"status": "404" , "message": "There was an error adding the book"}



#endpoint for getting a book 
@app.route("/api/get/<book_id>",methods=["GET"])
def getBook(book_id):
    json_cache = "bookcache.json"
    data = fetch_data(cache=cache,json_cache=json_cache,method="GET",book_id=book_id)

    return data

#endpoint for deleting a book
@app.route("/api/delete/<book_id>",methods=["DELETE"])
def deleteBook(book_id):
    #if the  deleted bookid is present in cache we remove it from cache
    with open("bookcache.json","r") as file:
        json_data = json.load(file)

    
    remove_from_cache(book_id,json_data)
        

    if books.delete_book(book_id):
        return {"status": "200", "message": "Book Succesfully deleted"}
    else:
        return {"status": "404" , "message": "There was an error deleting the book"}

if __name__ == "__main__":

    app.run(debug = True)
    


    