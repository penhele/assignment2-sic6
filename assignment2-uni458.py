from flask import Flask, jsonify, request
from pymongo.mongo_client import MongoClient
app = Flask(__name__)

uri = "mongodb+srv://uni458:BelajarSastraMesin@cluster-sic.jdscv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster-SIC"
client = MongoClient(uri)
db = client['iot_data']
collection = db['sensor']

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

@app.route('/iot_data', methods =['POST'])
def receive_iot_data():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    try:
        collection.insert_one(data)
        return jsonify({"message": "Data inserted successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)