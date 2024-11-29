import os
import chromadb

class Database:
    
    #l'instance roule sur cette adresse
    def __init__(self, host="172.17.0.3", port="8000"):
        self.host = host  # IP address
        self.port = port  # Port number
        self.client = self.get_client_db()
        self.collection = "antoine_test"

    def get_client_db(self):
        #Connexion BD vector
        client = chromadb.HttpClient(host=self.host, port=self.port) 
        return client

    def get_collection(self, colname):
        #Return collection
        return self.client.get_collection(colname) 
    

    def reset_collection(self):
        #reset la collection et ajuste
        #https://docs.trychroma.com/guides

        self.client.delete_collection(self.collection)

        self.client.create_collection(
            name=self.collection,
            metadata={"hnsw:space": "cosine"}
            
            )
