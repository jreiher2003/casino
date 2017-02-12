import pymongo 
from pymongo import MongoClient 
from datetime import datetime


conn = MongoClient("mongodb://finn:finn7797@localhost:27017/casino")
db = conn.casino.test_col

# blog_record = {}
blog_record = {
    "author": "erlichson",
    "body": "This is a test body",
    "comments": [
            {
            "body":"this is a comment",
            "email": "jeffreiher@gmail.com",
            "author": "Jeff Reiher 1"
            },
            {
            "body":"This is another comment",
            "email":"jreiher2003@yahoo.com",
            "author":"Finn Gotti"
            }
        ],
    "date": datetime.utcnow(),
    "permalink": "This_is_a_test_Post", 
    "tags": ["cycling", "mongodb", "swimming"],
    "title": "This is a test Post"
    }
# blog_record2 = {}
blog_record2 = {
    "author": "mcnuts",
    "body": "This is body of second record",
    "comments": [
            {
            "body":"this is a comment record 2",
            "email": "jeff_record2@gmail.com",
            "author": "Jeff Reiher 2"
            },
            {
            "body":"This is another comment 2",
            "email":"reiher@yahoo.com",
            "author":"Gotti record 2"
            }
        ],
    "date": datetime.utcnow(),
    "permalink": "This_is_a_test_Post_record_2", 
    "tags": ["howbahdaw", "bitchassness", "fucking"],
    "title": "This is a test Post Record 2"
    }
db.insert(blog_record)
db.insert(blog_record2)
conn.close()


