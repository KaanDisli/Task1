from flask import Flask, request, jsonify
from services import book_service
import json
import cachetools
from cachetools import TTLCache
import copy
from datetime import datetime
import redis
from BooksAPI import books


redis_client = redis.Redis(host='localhost',port = 6379, db=0)




def redis_client_get():
        byte_string = redis_client.get("library_data")
        json_data = None
        if byte_string != None:
            json_string = byte_string.decode('utf-8')
            json_data = json.loads(json_string)
        return json_data

def log(message):
        current_time = datetime.now().time()
        with open("logs.txt","a") as file:
            file.write(f'{message} : {current_time}\n')
        
def add_to_cache(body):
    print("this is the body")
    print(body)
    byte_string = redis_client.get("library_data")
    json_data = None
    if byte_string != None:
        json_string = byte_string.decode('utf-8')
        json_data = json.loads(json_string)
        json_data = json.dumps(json_data)
        redis_client.set("library_data",json_data,ex=900)
        
    else:
        redis_client.set("library_data",body,ex=900)
        

    
#we update the book with the id passed as parameter from the cache
def update_in_cache(id,list,title,author,price,category):
    id = int(id)
    for elem in list:
        id_, title_, author_, price_, category_ = elem
        if id_ == id:   
            #update the cache
            list.remove(elem)
            log(f"Book  with id: {id} was updated in cache.\n Previously: {elem} \n Now: {(id ,title, author, price,category)}")
            list.append((id ,title, author, price,category)) 
            json_data = json.dumps(list)
            redis_client.set("library_data",json_data,ex=900)
            return True
            
                
    return False


#we remove the book with the id passed as parameter from the cache
def remove_from_cache(id,list):
    id = int(id)
    for elem in list:
        id_, title_, author_, price_, category_ = elem
        if id_ == id:   
            list.remove(elem)
            log(f"Book with id: {id} was removed from cache ")
            json_data = json.dumps(list)
            redis_client.set("library_data",json_data,ex=900)
            return True
            
                
    return False


#Here we iterate over the books in the cache to see if the book with the id passed as a parameter exists
def search_id_list(id,list):
    id = int(id)
    for elem in list:
        id_, title, author, price, category = elem
        if id_ == id:   
            log(f"Book with id: {id} was found in local cache ")
            return True, {
                "id":id,"title":title,"author":author,"price":price, "category":category
            }
    return False, {"status": 403, "message":"Book does not exist"}

def search_category_cache(category,list):
    new_list = []
    for elem in list:
        id_, title_, author_, price_, category_ = elem
        if category == category_:
            new_list.append({
                "id":id_,"title":title_,"author":author_,"price":price_, "category":category_
            }

            )
    json_string = json.dumps(new_list)
    if new_list != []:
        log(f"Book with category: {category} was found in local cache ")
        
        return True, json_string
    else:
        return False, json_string

def fetch_data(*,method = "GET",book_id,category):
    #if the cache has expired we need to make a db query for the json data
    try:
        #if the cache has not expired we open the local cache
        byte_string = redis_client.get("library_data")
        if byte_string != None:
            json_string = byte_string.decode('utf-8')

            # Load the JSON string into a Python object
            json_data = json.loads(json_string)
        else:
            json_data = None
        print("Fetched data from local cache")
        log("Fetched books from local cache")

    except(FileNotFoundError,json.JSONDecodeError) as e:
        log(f"Problem with local cache:  {e}")
        print(f'Problem with local cache:  {e}')
        json_data = None 
        #if the book can be found in the local cache we return it, if not we expire the timer on the cache make a db query
    if json_data != None:
        if category == None:
            status, message =  search_id_list(book_id,json_data) 
            if status:
                return message
            else:
                json_data = None
        else:
            json_data = None

    if json_data == None:
        print("Creating Local cache ")
        log("Creating Local cache")
        if method == "GET":
            #we make the db query here
            json_data = books.get_all_books()   
            redis_client.set("library_data", json.dumps(json_data), ex=900)
    #after making our query and writing it in the local cache we return if it is present as a book or not    
    if category == None:
        status, message =  search_id_list(book_id,json_data) 
    else: 
        status, message =  search_category_cache(category,json_data) 
    return message



def check_params_add(body):
    l = ['title','author','price','category']
    for elem in l: 
        if elem not in body:
            return False
    return True