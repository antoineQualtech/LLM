import os
import sys
import ollama
import Database
import Embedding
import Program

PROMPT_TEMPLATE = """
        Answer the question based only on the following context:

        {context}

        ---

        Answer the question based on the above context: {question}
        """

class Program:

    def __init__(self):
        self.folderpath = "data"
        self.collection = "antoine_test"
        self.db = Database.Database()
        self.embedder = Embedding.Embedding()

    #loop les fichiers dans le dossier data
    def readfiles(self):
        client =  self.db

        ####delete remove#######
        client.get_client_db().delete_collection(self.collection)
        client.get_client_db().create_collection(self.collection)

        #directory = os.fsencode("data")
        for file in os.listdir(self.folderpath):
            filename = os.fsdecode(file)
            filepath = os.path.join(self.folderpath, filename)

            # Process les PDF files
            if filename.endswith(".pdf"):
                #print(f"Filepath: {filepath}")
                try:  
                    self.processfile(filepath)
                except Exception as e:
                     print(f"👉 Could not add {filepath} to documents : " + repr(e))    

        #myCollection =  client.getCollection(colname=self.collection)
        #print(client.getCollection(include=[]) )    

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

        #print(new_chunks[0].metadata["id"])
        #print(new_chunks[0].metadata)
        #print(new_chunks[0].page_content)
        
        if len(new_chunks):
            print(f"👉 Adding new documents: {len(new_chunks)} from source :"+filepath)
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
                print(f"Error while embedding: {e}")
        
    #questions 
    def questionllm(self,question):
        #l'instance de la db
        client = self.db.client

        collection = client.get_collection(name=self.collection)

        query = question
        response  = ollama.embeddings(model="nomic-embed-text", prompt=query)

        results = collection.query(
            query_embeddings=[response["embedding"]],
            n_results=5
        )

        dataForAi = results['documents'][0][0]

        docs = results['documents'][0]
        sources = results['metadatas'][0]

        docsWithUris = []
        i = 0
        for source in sources:  
            docsWithUris.append({"uri":source["source"],"doc":docs[i]})
            i+=1


        #print(results)
        output = ollama.generate(
            model="llama2",
            prompt=f"Using this data: {dataForAi}. Respond to this prompt: {query}"
        )

        print("Réponse AI 👉 "+output['response'])
        #print(output['response'])
        print("")
        print("")
        print("Les sources 👇  ")
        print("")
        for docWithUri in docsWithUris:
            print("🫱🫱🫱🫱")
            print( "URI : "+ str(docWithUri['uri']) + " 👉 " +" DOC : "+ str(docWithUri['doc']))
            print("🫱🫱🫱🫱")
            print("")

    if __name__ == "__main__":
        program = Program.Program()

        print("test---------")
        program.readfiles()
        #question = "Where is Qualtech?"
        #result = program.questionllm(question) 

        #print(result)
        