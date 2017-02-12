import os
import pymongo 
from pymongo import MongoClient 

def connect_mongo():
    conn = MongoClient(os.environ['MONGO_DB'])
    db = conn.casino 
    return db.test_col 

def connect_mongo_gwages():
    conn = MongoClient(os.environ['MONGO_DB'])
    db = conn.casino 
    return db.gwages
