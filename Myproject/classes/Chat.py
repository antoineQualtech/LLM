import ollama

class Chat: 
    
    def __init__(self, db, collection):
        self.db = db
        self.collection = collection

    #poser les questions
    def questionllm(self, question,withLLMAnswer,nbSource):

        #L'instance de la DB
        client = self.db.client
        #collection source
        collection = client.get_collection(name=self.collection)

        #les questions
        query = question
        #embed la question
        response = ollama.embeddings(model="nomic-embed-text", prompt=query)


        #requete vecteur
        results = collection.query(
            query_embeddings=[response["embedding"]],
            n_results= int(nbSource)
        )

        #les recu donnees
        dataForAi = results['documents'][0][0]
        docs = results['documents'][0]
        sources = results['metadatas'][0]

        #list les sources pour et premache les donnees
        docsWithUris = []
        for i, source in enumerate(sources):
            docsWithUris.append({"uri": source["source"], "doc": docs[i]})

        #promt le llm
        output = ""
        if withLLMAnswer == True :
                output = ollama.generate(
                model="llama2",
                prompt=f"Using this data: {dataForAi}. Respond to this prompt: {query}"
            )
        


        #print("Réponse AI  " + output['response'])
        #print("\n\nLes sources   \n")
        #for docWithUri in docsWithUris:
        #    print("﫱﫱﫱﫱")
        #    print(f"URI : {docWithUri['uri']}  DOC : {docWithUri['doc']}")
         #   print("﫱﫱﫱﫱")
         #   print("")

        return output, docsWithUris
