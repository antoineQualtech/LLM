from flask import Flask, request, jsonify
from classes.Program import Program
import json
import os

app = Flask(__name__)

program = Program() # le programme 
PASSWORD = "siado123"


#point d'API pour embed les fichiers nécessite un mot de passe passé en paramètres éviter les erreurs
@app.route("/embed-files/<passw>", methods=["GET"])
def embedFiles(passw):

    retData = {
        "msg" : "",
    } 

    if passw == PASSWORD:
        #executer le embedding
        try:
            program.process_directory()
            retData["msg"] = "Embedding done"
            return jsonify(retData), 200
        except Exception as e:
            retData["msg"] = f"Error during embedding: {str(e)}"
            return jsonify(retData), 500
    else:
        retData["msg"] = "Password Invalid"     
        return jsonify(retData) , 401

#route pour poser les questions
@app.route("/q-a",  methods=["POST"])
def questionLLM():

    data = request.get_json()

    if not data or "question" not in data:
        return jsonify({"msg": "Missing 'question' in request body"}), 400

    question = data["question"]

    retData = {
        "msg": "",
        "response": "",
        "sources": [],
    }

    try:
        # Use the program to ask the question
        response, docs_with_uris = program.question_processor.questionllm(question)
        retData["response"] = response
        retData["sources"] = docs_with_uris
    except Exception as e:
        retData["msg"] = f"Error processing question: {str(e)}"
        return jsonify(retData), 500

    return jsonify(retData), 200

#reset la database
@app.route("/reset/<passw>",  methods=["DELETE"])
def resetDB(passw):

    retData = {
        "msg" : "",
    } 

    if passw == PASSWORD:
        retData["msg"] = "Database reset"
        program.db.get_client_db().delete_collection(program.collection)
        program.db.get_client_db().create_collection(program.collection)
        return jsonify(retData), 200
    else:
        retData["msg"] = "Password Invalid"     
        return jsonify(retData) , 401

#modifie le config file
@app.route('/update-config', methods=['POST'])
def update_config():
    print(os.getcwd())
    try:
        incoming_data = request.get_json()

        if not incoming_data or not all(key in incoming_data for key in ['chunksize', 'overlap', 'nbdossier']):
            return jsonify({"msg": "Missing required keys in the request body"}), 400

        with open('api/configfile/config.json', 'r') as file:
            data = json.load(file)

        data['chunksize'] = incoming_data['chunksize']
        data['overlap'] = incoming_data['overlap']
        data['nbdossier'] = incoming_data['nbdossier']

        with open('api/configfile/config.json', 'w') as file:
            json.dump(data, file, indent=4)

        return jsonify({"msg": "Config updated successfully!"}), 200

    except FileNotFoundError:
        return jsonify({"msg": "Config file not found."}), 404
    except json.JSONDecodeError:
        return jsonify({"msg": "Error decoding JSON data from the config file."}), 500
    except Exception as e:
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500

#get le config et affiche
@app.route('/get-config', methods=['GET'])
def get_config():
    try:
        
        with open('api/configfile/config.json', 'r') as file:
            data = json.load(file)

        
        return jsonify(data), 200

    except FileNotFoundError:
        return jsonify({"msg": "Config file not found."}), 404
    except json.JSONDecodeError:
        return jsonify({"msg": "Error decoding JSON data from the config file."}), 500
    except Exception as e:
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0',port='5205',debug=False)    