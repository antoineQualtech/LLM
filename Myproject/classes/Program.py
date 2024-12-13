import os
import sys
import ollama
import json
from classes.Embedding import Embedding
from classes.Database import Database
from classes.Chat import Chat
from classes.FileLoader import FileLoader


class Program:

    # 10.4.100.77 numéro de serveur  "//10.4.100.77/AntoineTMP/"
    def __init__(self):
        self.db = Database()
        self.embedder = Embedding()
        self.collection = "antoine_test"
        self.folderpath = os.path.join('/', 'home', 'qualtechuser', 'ArchiveClient')
        self.directory_processor = FileLoader(
            self.db, self.embedder, self.collection, self.folderpath
        )
        self.question_processor = Chat(self.db, self.collection)

    def process_root(self):
        
         #limit a 5 temporairement
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
        

        
        dirs = os.listdir(self.folderpath)

        for filename in dirs[:nbdossier]:
            filepath = os.path.join(self.folderpath, filename)
            if os.path.isdir(filepath):
                self.directory_processor.process_directory(filepath)  

    def ask_question(self, question):
        self.question_processor.questionllm(question)

if __name__ == "__main__":
    program = Program()

    ##REMOVE
    #program.db.get_client_db().delete_collection(program.collection)
    #program.db.get_client_db().create_collection(program.collection)


    print("test---------")
    # program.process_directory()

    #question = "What is qualtech?"
    #program.ask_question(question)
    
