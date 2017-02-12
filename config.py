import os 

class BaseConfig(object):
    DEBUG = False 
    # MONGOALCHEMY_DATABASE = "casino"
    # MONGOALCHEMY_CONNECTION_STRING = "mongodb://finn:finn7797@localhost:27017/casino"

class DevelopmentConfig(BaseConfig):
    # MONGO_DB = "mongodb://finn:finn7797@localhost:27017/casino"
    DEBUG = True

class ProductionConfig(BaseConfig):
    DEBUG = False