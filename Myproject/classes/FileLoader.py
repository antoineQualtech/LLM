import os
import json

class FileLoader:

    def __init__(self, db, embedder, collection, folderpath):
        # 10.4.100.77 numéro de serveur  "//10.4.100.77/AntoineTMP/"
        self.folderpath = folderpath
        self.collection = collection
        self.db = db
        self.embedder = embedder
        self.log_file = "log.txt"

    #loop les fichiers dans le dossier data
    def process_directory(self, folderpath):
        try:
            dirs = os.listdir(folderpath)
        except Exception as e:
            print(f"Error reading directory {folderpath}: {repr(e)}")
            return

        # Process 
        for filename in dirs: 
            filepath = os.path.join(folderpath, filename)

            if os.path.isdir(filepath):
                self.process_directory(filepath)  # Recursive
            else:
                self.process_file(filepath)  

    #validation fichier pour processing
    def process_file(self, filepath):
        try:
        
            if filepath.endswith(".pdf"):
                self.processfile(filepath)  
                print(f"Processing PDF: {filepath}")
                self.log_to_file("->"+filepath)
            elif filepath.endswith(".docx"):
                self.processfile(filepath)  
                print(f"Processing DOCX: {filepath}")
                self.log_to_file("->"+filepath)
            elif filepath.endswith(".csv"):
                self.processfile(filepath)  
                print(f"Processing CSV: {filepath}")
                self.log_to_file("->"+filepath)
            elif filepath.endswith(".xlsx"):
                self.processfile(filepath)  
                print(f"Processing XLSX: {filepath}")
                self.log_to_file("->"+filepath)
            else:
                print(f"File type not supported: {filepath}")
        except Exception as e:
            print(f"Error processing file {filepath}: {repr(e)}")


    def log_to_file(self, message):
        try:
            with open(self.log_file, 'a') as log:
                log.write(message + '\n')
        except Exception as e:
            print(f"Error writing to log file: {repr(e)}")

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
                ##f = open("logs.txt", "w")
                ##f.close()
            except Exception as e:
                print(f"Error pendant l'embedding: {e}")
        else: 
            print("👉 Pas de new chunks fichier deja embeded")

