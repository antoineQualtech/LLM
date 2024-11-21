from langchain_community.document_loaders import PyPDFLoader # le file loader
from langchain_community.document_loaders.csv_loader import CSVLoader #csv
from langchain_community.document_loaders import Docx2txtLoader #docx
from langchain_text_splitters import RecursiveCharacterTextSplitter # pour split le text pour le chunking
#from langchain_community.document_loaders import UnstructuredPowerPointLoade #powerpoint
from langchain_community.document_loaders import UnstructuredExcelLoader #excel
from langchain_ollama import OllamaEmbeddings
import json

import ollama

class Embedding:

    def __init__(self):
        #embedder
        self.embedder = OllamaEmbeddings(model="nomic-embed-text")

    #load les PDF
    def loaddocument(self,filepath):
        if filepath.endswith(".pdf"):
            loader = PyPDFLoader(file_path=filepath)
            docs = loader.load()

        #si csv
        elif filepath.endswith(".csv"):
            loader = CSVLoader(file_path=filepath)
            docs = loader.load()

        #si DOCX
        elif filepath.endswith(".docx"):
            loader = Docx2txtLoader(file_path=filepath)
            docs = loader.load() 

        #si pptx
        #elif filepath.endswith(".pptx"):
         #   loader = UnstructuredPowerPointLoader(file_path=filepath)
          #  docs = loader.load()

        #si excel
        elif filepath.endswith(".xlsx"):
            loader = UnstructuredExcelLoader(file_path=filepath, mode="elements")
            docs = loader.load()

        return docs 

    #splitting le text 
    def textsplitting(self,docs):
        #config 
        chunksize = 200 #base
        overlap = 25 #base
        json_file_path = 'api/configfile/config.json'
        try:
            with open(json_file_path, 'r') as file:
                data = json.load(file)
                chunksize = data.get("chunksize")
                overlap = data.get("overlap")
        except FileNotFoundError:
            print("The file does not exist.")
        except json.JSONDecodeError:
            print("Error decoding the JSON data.")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")       

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunksize,
            chunk_overlap = overlap

        )

        texts = text_splitter.split_documents(docs)
        return texts
    
    #calcule des ids pour les différent chunks éviter de recréer en double les chunks et aide l'indexation
    def calculate_chunk_ids(self,chunks):
        last_page_id = None
        current_chunk_index = 0

        for chunk in chunks:
            source = chunk.metadata.get("source")
            page = chunk.metadata.get("page")
            current_page_id = f"{source}:{page}"

            if current_page_id == last_page_id:
                current_chunk_index += 1
            else:
                current_chunk_index = 0

            chunk_id = f"{current_page_id}:{current_chunk_index}"
            last_page_id = current_page_id

            chunk.metadata["id"] = chunk_id

        return chunks
    
    #création des embeddings
    def embeddoc(self, docs):
        #print(docs)
        embeddings = self.embedder.embed_documents(docs)
        return embeddings
    

    def embeddingfunc(self):
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        return embeddings.get('embeddings', [])
