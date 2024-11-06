from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import cellPhoneS.cellPhoneS.process_data as prd
import pv
import config 
# Function to check if a database exists
def database_exists(client, db_name):
    return db_name in client.list_database_names()

# Function to check if a collection exists in a database
def collection_exists(db, collection_name):
    return collection_name in db.list_collection_names()

if __name__ == "__main__":
    uri = config.mongo_uri

    client = MongoClient(uri, server_api=ServerApi('1'))

    db_name = "Laptop_DB"

    collection_name = "Laptop"
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")

        # Check if the database exists
        if not database_exists(client, db_name):
            print(f"Database '{db_name}' does not exist. It will be created.")
            db = client[db_name]
        else:
            print(f"Database '{db_name}' already exists.")
            db = client[db_name]

        collection = db[collection_name]
        
        documents = prd.start_process() + pv.process_all()
  
        result = collection.insert_many(documents)
    
    except Exception as e:
        print(e)