import os
import chromadb

class Database:
    
    #l'instance roule sur cette adresse
    def __init__(self, host="172.17.0.3", port="8000"):
        self.host = host  # IP address
        self.port = port  # Port number
        self.client = self.get_client_db()

    def get_client_db(self):
        #Connexion BD vector
        client = chromadb.HttpClient(host=self.host, port=self.port)
        return client

    def get_collection(self, colname):
        #Return collection
        return self.client.get_collection(colname) 
