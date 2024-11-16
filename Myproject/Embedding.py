from langchain_community.document_loaders import PyPDFLoader # le file loader
from langchain_text_splitters import CharacterTextSplitter # pour split le text pour le chunking
from langchain_ollama import OllamaEmbeddings
import ollama

class Embedding:

    def __init__(self):
        self.embedder = OllamaEmbeddings(model="nomic-embed-text")

    def loaddocument(self,filepath):
        #print(filepath)
        loader = PyPDFLoader(filepath)
        docs = loader.load()
        return docs
    
    def textsplitting(self,docs):
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=500,
            chunk_overlap=20,
            length_function=len,
            is_separator_regex=False,
        )
        texts = text_splitter.split_documents(docs)
        return texts
    
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
    
    def embeddoc(self, docs):
        #print(docs)
        embeddings = self.embedder.embed_documents(docs)
        return embeddings
    
    def embeddingfunc(self):
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        return embeddings.get('embeddings', [])
