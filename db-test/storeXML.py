import pymongo
import os

# Connect to the MongoDB
client = pymongo.MongoClient(host='localhost', port=27017, username='admin', password='password')
db = client['test']
collection = db['xml']

# Read the XML file
with open('ruadapega.rou.xml', 'r') as file:
    xml = file.read()

collection.delete_many({})

# Store the XML file in the MongoDB
collection.insert_one(
    {
        'user': 'test',
        'xml': xml
    }
)

# Retrieve the XML file from the MongoDB
data = collection
for doc in data.find():
    print(doc['xml'])
    # Write the XML file
    with open('test.xml', 'w') as file:
        file.write(doc['xml'])

# Close the connection
client.close()
