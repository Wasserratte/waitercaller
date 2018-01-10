import pymongo

client = pymongo.MongoClient()	#Connection to MongoDB

c = client['waitercaller']	#Connect to the database waitercaller

print c.users.create_index("email", unique=True) 

print c.requests.create_index("table_id", unique=True)

		#In the collection (variable c) we create the index and
		#and pass in the field name to create the index. To the
		#the index we add a unique constraint.
		#We write in the collection users and requests.
