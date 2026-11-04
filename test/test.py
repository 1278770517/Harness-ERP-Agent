from pymongo import MongoClient

client = MongoClient(
    "mongodb://admin:123456@127.0.0.1:27017/?authSource=admi"
)

print(client.admin.command("ping"))