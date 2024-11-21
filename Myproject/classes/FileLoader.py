import os
import json

class FileLoader:

    def __init__(self, db, embedder, collection, folderpath):
        # 10.4.100.77 numéro de serveur  "//10.4.100.77/AntoineTMP/"
        self.folderpath = folderpath
        self.collection = collection
        self.db = db
        self.embedder = embedder

    #loop les fichiers dans le dossier data
    def process_directory(self, folderpath=None):
        #print(os.getcwd())
        nbdossier = 5 #base
        json_file_path = 'api/configfile/config.json'
        try:
            with open(json_file_path, 'r') as file:
                data = json.load(file)
                nbdossier = data["nbdossier"]
        except FileNotFoundError:
            print("The file does not exist.")
        except json.JSONDecodeError:
            print("Error decoding the JSON data.")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")     

        client = self.db
        
        if folderpath is None:
            folderpath = self.folderpath  
        
        dirs = os.listdir(folderpath)

        #limit a 5 temporairement
        try:
            for filename in dirs[:nbdossier]:
                filepath = os.path.join(folderpath, filename)
                
                #si dir rentre  
                if os.path.isdir(filepath):
                    self.process_directory(filepath)  

                #si pdf
                elif filename.endswith(".pdf"):
                    try:
                        self.processfile(filepath)
                    except Exception as e:
                        print(f"👉 Ne peux pas ajouter {filepath} aux documents: " + repr(e))

                #si docx
                elif filename.endswith(".csv"): 
                    try:
                        self.processfile(filepath)
                    except Exception as e:
                        print(f"👉 Ne peux pas ajouter {filepath} aux documents: " + repr(e))  

                #si docx
                elif filename.endswith(".docx"):
                    try:
                        self.processfile(filepath)
                    except Exception as e:
                        print(f"👉 Ne peux pas ajouter {filepath} aux documents: " + repr(e)) 

                #power point    
                #elif filename.endswith(".pptx"):
                    #try:
                        #self.processfile(filepath)
                    #except Exception as e:
                     #   print(f"👉 Ne peux pas ajouter {filepath} aux documents: " + repr(e))                

                #excel   
                elif filename.endswith(".xlsx"):
                    try:
                        self.processfile(filepath)
                    except Exception as e:
                        print(f"👉 Ne peux pas ajouter {filepath} aux documents: " + repr(e)) 



        except Exception as e:
            print(f"Problème lorsqu'on process {folderpath}: {repr(e)}")

    #process le file et insert in db
    def processfile(self,filepath):
        #access la db
        client =  self.db

        #ma collection
        myCollection =  client.get_collection(colname=self.collection)
     
        #load le file
        docs = self.embedder.loaddocument(filepath)

        #text splitting (chunking)
        chunks = self.embedder.textsplitting(docs)
        #rint(chunks)

        chunks_with_ids = self.embedder.calculate_chunk_ids(chunks)
        #print(chunks)

        ##valider si les docs sont déjà là
        #existing_items = myCollection.get(include=["embeddings","metadatas","documents"]) 
        existing_items = myCollection.get(include=[])
        #print(myCollection.get(include=[])) 

        existing_ids = set(existing_items["ids"])
        #print(f"Number of existing documents in DB: {len(existing_ids)}")

        # ajoute si le id existe pas
        new_chunks = []
        for chunk in chunks_with_ids:
            if chunk.metadata["id"] not in existing_ids:
                new_chunks.append(chunk)
        
        if len(new_chunks):
            print(f"👉 Chunks créés : {len(new_chunks)} du fichier :"+filepath)
            new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
            new_chunk_metadatas = [chunk.metadata for chunk in new_chunks]
            new_chunk_docs = [chunk.page_content for chunk in new_chunks]
            embeddings = []

            try:
                #embed
                embeddings = self.embedder.embeddoc(new_chunk_docs)

                #ajout à la db
                myCollection.add(
                ids=new_chunk_ids,
                metadatas=new_chunk_metadatas,
                documents=new_chunk_docs,
                embeddings=embeddings
            )  
                #print(myCollection.get(include=["metadatas"]) )

            except Exception as e:
                print(f"Error pendant l'embedding: {e}")
        else: 
            print("👉 Pas new chunks fichier embeded")