import os
import chromadb

class Database:

    def __init__(self):
        self.host = "localhost" #ip
        self.port = "8000" #port
        self.client = self.getClientDB()

    def getClientDB(self):
        #persistent db
        client =  chromadb.HttpClient(host=self.host, port = self.port)
        return client

    def getCollection(self,colname):  
        #create la collection
        #collection = client.create_collection("antoine_test")
        #get list collections
        #collections = self.client.list_collections()
        #print(collections[0])
        
        myCollection =  self.client.get_collection(colname)
        return myCollection   
