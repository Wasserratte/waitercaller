import pymongo
from bson.objectid import ObjectId

DATABASE = "waitercaller"	#Global variable with the name of our database

class DBHelper:

    def __init__(self):

        client = pymongo.MongoClient() 	#Python object with MongoClient(), so we can run operations
        self.db = client[DATABASE]	#Connect to the specified database

    def get_user(self, email):

        return self.db.users.find_one({"email": email})		#To grab data from the database

    def add_user(self, email, salt, hashed):	#Add new user

        self.db.users.insert({"email": email, "salt": salt, "hashed": hashed})

    def add_table(self, number, owner):	#MockDB assign a unique _id. We return it to create the table_url

        new_id = self.db.tables.insert({"number": number, "owner": owner})
        return new_id

    def update_table(self, _id, url):	#We update a specific content

        self.db.tables.update({"_id": _id}, {"$set": {"url": url}})

    def get_tables(self, owner_id):	#Get all tables as a generator and convert it to a list to pass it to the template

        return list(self.db.tables.find({"owner": owner_id}))

    def get_table(self, table_id): #We use the ObjectId from bson to pass in the table_id from the url-string

        return self.db.tables.find_one({"_id": ObjectId(table_id)})

    def delete_table(self, table_id):	#Delete table by passing the table_id string into the ObjectId

        self.db.tables.remove({"_id": ObjectId(table_id)})

    def add_request(self, table_id, time):	#Inser creates new collection request, use data from collection table

        table = self.get_table(table_id)

        try:
            self.db.requests.insert({"owner": table['owner'], "table_number": table['number'], "table_id": table_id, 
                "time": time})
            return True

        except pymongo.errors.DuplicateKeyError:
            return False

    def get_requests(self, owner_id):

        return list(self.db.requests.find({"owner": owner_id}))

    def delete_request(self, request_id):

        self.db.requests.remove({"_id": ObjectId(request_id)})


