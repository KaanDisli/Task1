from flask import Flask, request, jsonify
from services import book_service,book_functions
import json
import cachetools
from cachetools import TTLCache
import copy
from datetime import datetime
from BooksAPI import books

def log(message):
        current_time = datetime.now().time()
        with open("logs.txt","a") as file:
            file.write(f'{message} : {current_time}\n')
        


#we update the book with the id passed as parameter from the cache
def update_in_cache(id,list,title,author,price,category):
    duplicate_list = copy.deepcopy(list)
    id = int(id)
    for elem in list:
        id_, title_, author_, price_, category_ = elem
        if id_ == id:   
            #update the cache
            duplicate_list.remove(elem)
            log(f"Book  with id: {id} was updated in cache.\n Previously: {elem} \n Now: {(id ,title, author, price,category)}")
            duplicate_list.append((id ,title, author, price,category)) 
            json_data = duplicate_list
            with open("bookcache.json","w") as file:
                json.dump(json_data,file)
            return True
                
    return False


#we remove the book with the id passed as parameter from the cache
def remove_from_cache(id,list):
    duplicate_list = copy.deepcopy(list)
    id = int(id)
    for elem in list:
        id_, title_, author_, price_, category_ = elem
        if id_ == id:   
            duplicate_list.remove(elem)
            log(f"Book with id: {id} was removed from cache ")
            json_data = duplicate_list
            with open("bookcache.json","w") as file:
                json.dump(json_data,file)
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

def fetch_data(*,cache,json_cache, method = "GET",book_id,category):
    #if the cache has expired we need to make a db query for the json data
    if cache['not_expired'] != True: 
        json_data = None  
    else:
        try:
            #if the cache has not expired we open the local cache
            with open(json_cache,"r") as file:
                json_data = json.load(file)
                print("Fetched data from local cache")
                log("Fetched books from local cache")
                #if the book can be found in the local cache we return it, if not we expire the timer on the cache make a db query
                if category == None:
                    status, message =  search_id_list(book_id,json_data) 
                else:
                    json_data = books.get_all_books()
                    with open("bookcache.json","w") as file:
                        json.dump(json_data,file)
                    status, message =  False, ""
                if status:
                    return message
                else:
                    cache.clear()
                    json_data = None
        except(FileNotFoundError,json.JSONDecodeError) as e:
            log(f"Problem with local cache:  {e}")
            print(f'Problem with local cache:  {e}')
            json_data = None 

    if json_data == None:
        print("Creating Local cache ")
        log("Creating Local cache")
        if method == "GET":
            #we make the db query here
            json_data = books.get_all_books()                
            with open(json_cache,"w") as file: 
                #we need to set the cache timer again now that we have gotten the new data
                cache['not_expired'] = True
                #we write the new data into our local cache
                json.dump(json_data,file)
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